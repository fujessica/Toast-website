from flask import Flask, flash, redirect, render_template, request, session, abort
import sqlite3

app = Flask(__name__)
app.secret_key = "super secret key"

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!"


@app.route('/login', methods=['POST'])
def do_admin_login():
    connection = sqlite3.connect('toast.db')
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM users WHERE username = 'jessicafu16'")
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        username = str(request.form['username'])
        return username
    else:
        flash('wrong password!')
    return home()


@app.route('/myreviews')
def user_reviews():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        connection = sqlite3.connect('toast.db')
        cursor = connection.cursor()
        cursor.execute("SELECT review FROM reviews WHERE user_id = '1'")
        reviews = cursor.fetchall()
        return render_template('myreviews.html', reviews = reviews)


@app.route('/reviews')
def show_all_reviews():
    connection = sqlite3.connect('toast.db')
    cursor = connection.cursor()
    cursor.execute('SELECT toast.description, review, username FROM Reviews JOIN Toast ON reviews.toast_id = toast.id JOIN Users ON reviews.user_id = users.id')
    reviews = cursor.fetchall()
    return  render_template("reviews.html", reviews = reviews)



if __name__ == "__main__":
    app.run(debug = True)

