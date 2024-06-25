from flask import Flask, render_template, request, session, redirect, url_for
import hashlib
import sqlite3


app = Flask(__name__)
app.secret_key = "super secret key"


'''functions'''

def index():
    if 'username' in session:
        return redirect(url_for('user_reviews'))
    else:
        return redirect(url_for('signup'))

def sql_queries(query, option):
    connection = sqlite3.connect('toast.db')
    cursor = connection.cursor()
    cursor.execute(query)
    if option == 0:
        result = cursor.fetchone()
        return result
    elif option == 1:
        result = cursor.fetchall()
        return result
    elif option == 2:
        connection.commit()
    connection.close()

def hash_password(password):
    password_hash = hashlib.sha256((password ).encode('utf-8')).hexdigest()
    return password_hash

def has_numbers(password):
    return any(i.isdigit() for i in password)



'''routes'''

@app.route('/')
def homepage():
    return render_template('home.html')

    
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method =='GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        query = "SELECT password FROM users WHERE username = '{}'".format(username)
        key = sql_queries(query, 0)
        if key is None:
            error_message = 'user does not exist'
            return render_template('login.html', error_message = error_message)
        elif key[0] == hashed_password:
            session['username'] = username 
            return redirect(url_for('user_reviews'))
        else:
            error_message = 'incorrect password'
            return render_template('login.html', error_message = error_message)


@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        session["username"] = request.form['username']
        password = request.form['password']
        if len(password) > 8 and len(username > 8):
            #Mike Rhodes - Stack overflow verfication that username is not taken already
            query = "SELECT username FROM users WHERE username = '{}'".format(username)
            result = sql_queries(query, 0)
            if result is not None:
                error_message = 'username is taken'
                return render_template('signup.html', error_message = error_message)
            else:
                password = hash_password(password)
                query = "INSERT INTO users(username, password) VALUES('{}', '{}')".format(username, password)
                sql_queries(query, 2)
                session['username'] = username
                return redirect(url_for('homepage'))
        elif len(username)<8:
            error_message = 'username is too short :C'
            return render_template('signup.html', error_message = error_message)
        elif has_numbers(password) == False:
            error_message = 'password must contain numbers'
            return render_template('signup.html', error_message = error_message)
        else:
            error_message = 'password too short'
            return render_template('signup.html', error_message = error_message)

        

@app.route('/create_review', methods = ['GET', 'POST'])
def create_review():
    if session['username'] is None:
        return redirect(url_for('login'))
    elif request.method == 'GET':
        query = 'SELECT * FROM Toast'
        toasts = sql_queries(query, 1)
        return render_template('create_reviews.html', toasts=toasts)
    elif request.method == 'POST':
        toast_id = request.form['toast_id']
        toast_review = request.form['review']
        username = session['username']
        query = "SELECT id FROM users WHERE username ='{}'".format(username)
        result = sql_queries(query, 0)
        user_id = result[0]
        query = "INSERT INTO reviews(user_id, review, toast_id) VALUES('{}', '{}', '{}')".format(user_id, toast_review, toast_id)
        sql_queries(query, 2)
        success_message = 'review submitted'
        return redirect(url_for('user_reviews', success_message = success_message))


@app.route('/logout')
def logout():
    session['username'] = None
    return redirect(url_for('homepage'))


@app.route('/my-reviews')
def user_reviews():
    if session["username"] is None:
        return render_template('signup.html')
    else:
        username = session["username"]
        query = "SELECT r.review FROM reviews as r join users as u on r.user_id = u.id WHERE u.username = '{}'".format(username)
        reviews = sql_queries(query, 1)
        return render_template('my_reviews.html', reviews = reviews, username = username)
    
    

@app.route('/reviews')
def show_all_reviews():
    query = 'SELECT description, review, username FROM Reviews JOIN Toast ON reviews.toast_id = toast.id JOIN Users ON reviews.user_id = users.id'
    reviews = sql_queries(query, 1)
    return render_template("reviews.html", reviews = reviews)

@app.route('/delete', methods = ['GET', 'POST'])
def delete_review():
    username = session['username']
    if request.method == 'GET':
        query = "SELECT t.id, description FROM reviews as r join users as u on r.user_id = u.id join Toast as t on r.toast_id = t.id WHERE u.username = '{}'".format(username)
        toasts = sql_queries(query, 1)
        return render_template('delete_review.html', toasts = toasts)
    elif request.method == 'POST':
        query = "SELECT id FROM Users WHERE username = '{}'".format(username)
        user_id = sql_queries(query, 0)[0]
        toast_id = request.form['toast_id']
        query = "DELETE FROM Reviews WHERE toast_id = '{}' and user_id =  '{}'".format(toast_id, user_id)
        sql_queries(query, 2)
        success_message = 'review deleted successfully'
        return render_template('my_reviews.html', success_message = success_message)



if __name__ == "__main__":
    app.run(debug = True)