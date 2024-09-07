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
        if 20 >= len(password
                     ) >= 8 and 20 >= len(username
                                          ) >= 8 and has_numbers(password
                                                                 ) is True:
            query = "SELECT username FROM users WHERE username = ?"
            result = sql_queries(query, 0, (username,))
            if result is not None:
                flash('username is taken')
                return redirect(url_for('signup'))
            else:
                session['username'] = username
                password = hash_password(password)
                query = "INSERT INTO users(username, password) VALUES(?, ?)"
                sql_queries(query, 2, (username, password))
                query = "SELECT id FROM Users WHERE username = ?"
                session['user_id'] = sql_queries(query, 0, (username,))[0]
                return redirect(url_for('my_reviews'))
        elif len(username) < 8 or len(username) > 20:
            flash('8< username <20 characters')
            return redirect(url_for('signup'))
        elif has_numbers(password) is False:
            flash('password needs 1 number')
            return redirect(url_for('signup'))
        elif len(password) > 20 or len(password) < 8:
            flash('8< password <20 characters')
            return redirect(url_for('signup'))
        else:
            flash('what the sigma')
            return redirect(url_for('signup'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        hashed_password = hash_password(request.form['password'])
        query = "SELECT password FROM users WHERE username = ?"
        key = sql_queries(query, 0, (request.form['username'],))
        if key is None:
            flash('incorrect username or password')
            return redirect(url_for('login'))
        elif hashed_password == key[0]:
            session['username'] = request.form['username']
            query = "SELECT id FROM Users WHERE username = ?"
            session['user_id'] = sql_queries(query, 0, (session['username'],))[0]
            return redirect(url_for('my_reviews'))
        else:
            flash('incorrect username or password')
            return redirect(url_for('login'))


@app.route('/my_reviews')
def my_reviews():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        query = "SELECT t.description, r.review, t.id, t.photo \
                 FROM reviews AS r \
                 JOIN Users as u ON r.user_id = u.id \
                 JOIN Toast AS t ON t.id = r.toast_id WHERE username = ?"
        username = session["username"]
        reviews = (sql_queries(query, 1, (username, )))
        return render_template('my_reviews.html',
                               reviews=reviews, username=username)


@app.route('/create_reviews', methods=['GET', 'POST'])
def create_review():
    if 'username' not in session:
        return redirect(url_for('signup'))
    elif request.method == 'GET':
        query = "SELECT id, description from Toast EXCEPT \
                 SELECT t.id, t.description FROM Toast as t \
                 JOIN reviews AS r ON r.toast_id = t.id JOIN users \
                 AS u ON u.id = r.user_id WHERE u.username = ?"
        toasts = sql_queries(query, 1, (session['username'], ))
        if len(toasts) == 0:
            flash('you have reviewed all toasts available')
            return redirect(url_for('my_reviews'))
        else:
            return render_template('create_reviews.html', toasts=toasts,
                                   username=session['username'])
    elif request.method == 'POST':
        toast_id = request.form['toast_id']
        toast_review = request.form['review']
        if len(toast_review) == 0:
            flash('review can not be blank')
            return redirect(url_for('create_review'))
        else:
            query = "INSERT INTO reviews(user_id, review, toast_id, approval)\
                     VALUES(?, ?, ?, ?)"
            sql_queries(query, 2, (session['user_id'], toast_review, toast_id, 0))
            flash('your review is being reviewed(haha)')
            return redirect(url_for('my_reviews'))


@app.route('/delete_reviews', methods=['GET', 'POST'])
def delete_review():
    if 'username' not in session:
        return redirect(url_for('signup'))
    else:
        if request.method == 'GET':
            username = session['username']
            query = "SELECT t.id, description, r.review FROM reviews as r\
                     JOIN users as u on r.user_id = u.id JOIN Toast AS t \
                        ON r.toast_id = t.id WHERE u.username = ?"
            toasts = sql_queries(query, 1, (username, ))
            if toasts == []:
                return redirect(url_for("my_reviews"))
            else:
                return render_template('delete_reviews.html', toasts=toasts)
        elif request.method == 'POST':
            toast_id = request.form['toast_id']
            query = "DELETE FROM Reviews WHERE toast_id = ? and user_id =  ?"
            sql_queries(query, 2, (toast_id, session['user_id']))
            flash('review deleted')
            return redirect(url_for('my_reviews'))


@app.route('/update_reviews', methods=['GET', 'POST'])
def update_reviews():
    if 'username' not in session:
        return redirect(url_for('signup'))
    else:
        if request.method == 'GET':
            username = session['username']
            query = "SELECT t.id, description, review \
                     FROM reviews as r JOIN users AS u \
                     ON r.user_id = u.id JOIN Toast AS t \
                     ON r.toast_id = t.id WHERE u.username = ?"
            toasts = sql_queries(query, 1, (username, ))
            return render_template('update_reviews.html', toasts=toasts)
        elif request.method == 'POST':
            review = request.form['review']
            if len(review) == 0:
                flash('review can not be blank')
                return redirect(url_for('update_reviews'))
            else:
                toast_id = request.form['toast_id']
                review = request.form['review']
                query = "UPDATE Reviews SET review = ?, approval = 0 \
                         WHERE toast_id = ? and user_id = ?"
                sql_queries(query, 2, (review, toast_id, session['user_id']))
                flash('your review is being reviewed haha')
                return redirect(url_for('my_reviews'))


@app.errorhandler(404)
def nopage(e):
    return render_template('404.html'), 404


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('show_all_reviews'))


if __name__ == "__main__":
    app.run(debug=True)
