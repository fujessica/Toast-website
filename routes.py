from flask import Flask, render_template, request, session
from flask import redirect, url_for, flash
from hashlib import sha256
import sqlite3


app = Flask(__name__)
app.secret_key = "super secret key"


def sql_queries(query, option, data=None):
    connection = sqlite3.connect('toast.db')
    cursor = connection.cursor()
    if data:
        cursor.execute(query, data)
    else:
        cursor.execute(query)
    if option == 0:
        result = cursor.fetchone()
        return result
    elif option == 1:
        result = cursor.fetchall()
        return result
    else:
        connection.commit()
    connection.close()


def hash_password(password):
    password_hash = sha256((password).encode('utf-8')).hexdigest()
    return password_hash


def has_numbers(password):
    return any(i.isdigit() for i in password)


@app.route('/')
def show_all_reviews():
    query = "SELECT t.id, description, review, username, t.photo \
             FROM Reviews as r JOIN Toast as t ON r.toast_id = t.id \
             JOIN Users as u ON r.user_id = u.id and approval = 1 \
             ORDER BY toast_id"
    reviews = sql_queries(query, 1)
    return render_template("reviews.html", reviews=reviews)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # all conditions fulfilled
        if 30 >= len(password
                     ) >= 8 and 30 >= len(username
                                          ) >= 8 and has_numbers(password
                                                                 ) is True:
            # checking for duplicate usernames by searching the database for
            # the username entered
            query = "SELECT username FROM users WHERE username = ?"
            result = sql_queries(query, 0, (username,))
            if result is not None:
                flash('Username is taken')
                return redirect(url_for('signup'))
            else:
                session['username'] = username
                password = hash_password(password)
                query = "INSERT INTO users(username, password, admin)\
                         VALUES(?, ?, ?)"
                sql_queries(query, 2, (username, password, 0))
                # setting up the user_id because I need to for queries in
                # later routes/functions
                query = "SELECT id FROM Users WHERE username = ?"
                session['user_id'] = sql_queries(query, 0, (username,)
                                                 )[0]
                # setting up admin for the changing navbar
                session['admin'] = 0
                return redirect(url_for('my_reviews'))
        elif has_numbers(password) is False:
            flash('Password must contain 1 number')
            return redirect(url_for('signup'))
        else:
            flash('Username and password may not be blank')
            return redirect(url_for('signup'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        # hashing the password so it matches the already
        # hashed password in the database
        hashed_password = hash_password(request.form['password'])
        query = "SELECT password FROM users WHERE username = ?"
        key = sql_queries(query, 0, (request.form['username'],))
        # if no password was found
        if key is None:
            flash('Incorrect username or password')
            return redirect(url_for('login'))
        elif hashed_password == key[0]:
            # if the hashed password in the form matches the password in the
            # datbase
            session['username'] = request.form['username']
            query = "SELECT id, admin FROM Users WHERE username = ?"
            session['user_id'] = sql_queries(query, 0, (session['username'],)
                                             )[0]
            session['admin'] = sql_queries(query, 0, (session['username'],)
                                           )[1]
            return redirect(url_for('my_reviews'))
        else:
            flash('Incorrect username or password')
            return redirect(url_for('login'))


@app.route('/my_reviews', methods=['GET', 'POST'])
def my_reviews():
    if request.method == 'GET':
        # checking if the user is logged in or not
        if 'username' not in session:
            return redirect(url_for('login'))
        else:
            # selecting all reviews of a specific user
            query = "SELECT t.description, r.review, r.id, t.photo \
                    FROM reviews AS r \
                    JOIN Users as u ON r.user_id = u.id \
                    JOIN Toast AS t ON t.id = r.toast_id WHERE username = ?"
            reviews = (sql_queries(query, 1, (session["username"], )))
            return render_template('my_reviews.html',
                                   reviews=reviews,
                                   username=session['username'])
    if request.method == 'POST':
        if 'Delete_review' in request.form:
            query = "SELECT user_id FROM Reviews WHERE id = ?"
            review_user = sql_queries(query, 0,
                                      (request.form['review_id'], ))[0]
            # checking the review and user match by selecting the username
            # correlating with the review_id
            if review_user == session['user_id']:
                query = "DELETE FROM Reviews WHERE id = ?"
                sql_queries(query, 2, (request.form['review_id'], ))
                flash("Review has been deleted")
                return redirect(url_for("my_reviews"))
            else:
                flash('This is not your review')
                return redirect(url_for("my_reviews"))
        elif 'Update_review' in request.form:
            # making session['review_id'] becauase I need it for the update
            # reviews page
            session['review_id'] = request.form['review_id']
            return redirect(url_for('update_reviews'))


@app.route('/create_reviews', methods=['GET', 'POST'])
def create_review():
    if 'username' not in session:
        flash('Sign up or login to create reviews')
        return redirect(url_for('signup'))
    elif request.method == 'GET':
        # selecting all toasts except those that the user has reviewed because
        # I want to limit the user to one review per toast
        query = "SELECT id, description from Toast EXCEPT \
                 SELECT t.id, t.description FROM Toast as t \
                 JOIN reviews AS r ON r.toast_id = t.id JOIN users \
                 AS u ON u.id = r.user_id WHERE u.username = ?"
        toasts = sql_queries(query, 1, (session['username'], ))
        if len(toasts) == 0:
            flash('You have reviewed all toasts available')
            return redirect(url_for('my_reviews'))
        else:
            return render_template('create_reviews.html', toasts=toasts,
                                   username=session['username'])
    elif request.method == 'POST':
        toast_id = request.form['toast_id']
        toast_review = request.form['review']
        if len(toast_review) == 0:
            flash('Review can not be blank')
            return redirect(url_for('create_review'))
        else:
            # anti hacking measure in case someone decides to
            # change the toast_id
            connection = sqlite3.connect('toast.db')
            cursor = connection.cursor()
            query = 'SELECT id FROM Toast EXCEPT SELECT toast_id FROM Reviews \
                where user_id = ?'
            cursor.execute(query, (session['user_id'], ))
            result = cursor.fetchall()
            toasts = []
            # making a list toast ids that the user has not reviewed
            # and then seeing if the toast_id is within that list
            for i in result:
                toasts.append(i[0])
            toast_id = int(toast_id)
            if toast_id in toasts:
                query = "INSERT INTO reviews(user_id, review, toast_id, \
                         approval) VALUES(?, ?, ?, ?)"
                sql_queries(query, 2, (session['user_id'], toast_review,
                                       toast_id, 0))
                flash('Your review is pending approval')
                return redirect(url_for('my_reviews'))
            else:
                return redirect(url_for('create_review'))


@app.route('/update_reviews', methods=['GET', 'POST'])
def update_reviews():
    if 'username' not in session:
        return redirect(url_for('signup'))
    else:
        if request.method == 'GET':
            # checking if a review_id exists in the session from myreviews
            # to be used to fetch the data needed
            if 'review_id' not in session:
                flash('Please select a review to update')
                return redirect(url_for('my_reviews'))
            else:
                query = "SELECT t.id, t.description, review from Reviews AS r\
                        JOIN Users AS u ON r.user_id = u.id JOIN Toast AS t \
                        ON t.id = r.toast_id WHERE r.id = ?"
                data = sql_queries(query, 0, (session['review_id'], ))
                return render_template('update_reviews.html', data=data)
        elif request.method == 'POST':
            review = request.form['review']
            # checking if review is blank or contains only spaces by checking
            # length and eliminating the spaces and then checking the length
            if len(review) == 0 or len(review.lstrip(" ")) == 0:
                flash('Review can not be blank')
                return redirect(url_for('update_reviews'))
            else:
                toast_id = request.form['toast_id']
                review = request.form['review']
                query = "UPDATE Reviews SET review = ?, approval = 0 \
                         WHERE toast_id = ? and user_id = ?"
                sql_queries(query, 2, (review, toast_id, session['user_id']))
                flash('Your review is being reviewed haha')
                session.pop('review_id', None)
                return redirect(url_for('my_reviews'))


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if 'admin' in session:
        if session['admin'] == 0:
            return redirect(url_for('show_all_reviews'))
        elif session['admin'] == '1':
            if request.method == 'GET':
                query = "SELECT r.id, u.username, r.review \
                        FROM reviews AS r JOIN users AS u \
                        ON r.user_id = u.id WHERE approval = 0"
                reviews = sql_queries(query, 1)
                return render_template('admin.html', reviews=reviews)
            elif request.method == 'POST':
                if 'Update_review' in request.form:
                    query = "UPDATE Reviews SET approval = 1 WHERE id = ?"
                    sql_queries(query, 2, (request.form['review_id'], ))
                    return redirect(url_for('admin'))
                elif 'Delete_review' in request.form:
                    query = "DELETE FROM Reviews WHERE id = ?"
                    sql_queries(query, 2, (request.form['review_id'], ))
                    return redirect(url_for('admin'))
    else:
        return redirect(url_for('signup'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route('/logout')
def logout():
    # removes username and user_id from session
    # which is how routes check if a user is logged in
    session.clear()
    return redirect(url_for('show_all_reviews'))


if __name__ == "__main__":
    app.run(debug=True)
