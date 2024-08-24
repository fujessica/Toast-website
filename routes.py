from flask import Flask, render_template, request, session, redirect, url_for, flash, get_flashed_messages
from hashlib import sha256
import sqlite3


app = Flask(__name__)
app.secret_key = "super secret key"

'''functions'''

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


'''routes'''

@app.route('/')
def show_all_reviews():
    query = "SELECT t.id, description, review, username, t.photo FROM Reviews as r JOIN Toast as t ON r.toast_id = t.id JOIN Users as u ON r.user_id = u.id and approval = 1 order by toast_id"
    reviews = sql_queries(query, 1)
    return render_template("reviews.html", reviews=reviews)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if 20 >= len(password) >= 8 and 20 >= len(username) >= 8 and has_numbers(password) == True:
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
                return redirect(url_for('my_reviews'))
        elif len(username) < 8 or len(username) > 20:
            flash('username invalid')
            return redirect(url_for('signup'))
        elif has_numbers(password) == False or len(password) > 20 or len(password) < 8:
            flash('password invalid')
            return redirect(url_for('signup'))
        else:
            flash('what the sigma')
            return redirect(url_for('signup'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        query = "SELECT password FROM users WHERE username = ?"
        key = sql_queries(query, 0, (username,))
        if key is None:
            flash('user error')
            return redirect(url_for('login'))
        elif hashed_password == key[0]:
            session["username"] = username
            return redirect(url_for('my_reviews'))
        elif hashed_password == key[0]:
            session["username"] = username
        else:
            flash('incorrect password')
            return redirect(url_for('login'))


@app.route('/my_reviews')
def my_reviews():
    if 'username' not in session or session['username'] is None:
        return redirect(url_for('login'))
    else:
        query = "SELECT t.description, r.review, t.id, t.photo FROM reviews AS r JOIN Users as u ON r.user_id = u.id join Toast AS t ON t.id = r.toast_id WHERE username = ?"
        username = session["username"]
        reviews = (sql_queries(query, 1, (username, )))
        return render_template('my_reviews.html', reviews=reviews, username=username)


@app.route('/create_reviews', methods=['GET', 'POST'])
def create_review():
    username = session['username']
    if 'username' not in session or session['username'] is None:
        return redirect(url_for('signup'))
    elif request.method == 'GET':
        query = "SELECT id, description from Toast EXCEPT SELECT t.id, t.description FROM Toast as t JOIN reviews AS r ON r.toast_id = t.id JOIN users AS u ON u.id = r.user_id WHERE u.username = ?"
        toasts = sql_queries(query, 1, (username, ))
        if len(toasts) == 0:
            flash('you have reviewed all toasts available')
            return redirect(url_for('my_reviews'))
        else:
            return render_template('create_reviews.html', toasts=toasts, username=username)
    elif request.method == 'POST':
        toast_id = request.form['toast_id']
        toast_review = request.form['review']
        if len(toast_review) == 0:
            flash('review can not be blank')
            return redirect(url_for('create_review'))
        else:
            user_id_query = "SELECT id FROM users WHERE username = ?"
            user_id = sql_queries(user_id_query, 0, (username, ))[0]
            query = "INSERT INTO reviews(user_id, review, toast_id, approval) VALUES(?, ?, ?, ?)"
            sql_queries(query, 2, (user_id, toast_review, toast_id, 0))
            flash('your review is being reviewed(haha)')
            return redirect(url_for('my_reviews'))


@app.route('/delete_reviews', methods=['GET', 'POST'])
def delete_review():
    if 'username' not in session or session['username'] is None:
        return redirect(url_for('signup'))
    else:
        if request.method == 'GET':
            username = session['username']
            query = "SELECT t.id, description, r.review FROM reviews as r join users as u on r.user_id = u.id join Toast as t on r.toast_id = t.id WHERE u.username = ?"
            toasts = sql_queries(query, 1, (username, ))
            return render_template('delete_reviews.html', toasts=toasts)
        elif request.method == 'POST':
            query = "SELECT id FROM Users WHERE username = ?"
            username = session['username']
            user_id = sql_queries(query, 0, (username, ))[0]
            toast_id = request.form['toast_id']
            query = "DELETE FROM Reviews WHERE toast_id = ? and user_id =  ?"
            sql_queries(query, 2, (toast_id, user_id))
            return redirect(url_for('my_reviews'))



@app.route('/update_reviews', methods=['GET', 'POST'])
def update_reviews():
    if request.method == 'GET':
        username = session['username']
        query = "SELECT t.id, description, review FROM reviews as r join users as u on r.user_id = u.id join Toast as t on r.toast_id = t.id WHERE u.username = ?"
        toasts = sql_queries(query, 1, (username, ))
        return render_template('update_reviews.html', toasts=toasts)
    elif request.method == 'POST':
        if len(request.form['review']) >= 800:
            return redirect(url_for('update_reviews'))
        elif len(request.form['review']) == 0:
            flash('message can not be blank')
        else:
            username = session['username']
            toast_id = request.form['toast_id']
            review = request.form['review']
            query = "SELECT id FROM users WHERE username = ?"
            user_id = sql_queries(query, 0, (username,))[0]
            query = "UPDATE Reviews SET review = ?, approval = 0 WHERE toast_id = ? and user_id = ?"
            sql_queries(query, 2, (review, toast_id, user_id))
            return redirect(url_for('my_reviews'))

@app.route('/logout')
def logout():
    session['username'] = None
    return redirect(url_for('show_all_reviews'))


if __name__ == "__main__":
    app.run(debug=True)
