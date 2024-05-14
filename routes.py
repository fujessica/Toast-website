from flask import Flask, flash, redirect, render_template, request, session, abort
import sqlite3

app = Flask(__name__)
app.secret_key = "super secret key"

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "hallo"


@app.route('/login', methods=['POST'])
def do_admin_login():
        password = request.form['password'] 
        username = request.form['username']
        connection = sqlite3.connect('toast.db')
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = '{}'".format(username))
        key = cursor.fetchone()
        if key[0] == password:   
            session['logged_in'] = True
            return(home())
        else:
            return 'wrong password!'



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

