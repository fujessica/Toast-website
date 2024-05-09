from flask import Flask, render_template
import sqlite3


app = Flask(__name__)

@app.route('/')

@app.route('/home')
def home():
    return 'home'

@app.route('/login')
def create_user():
    return(render_template('login.html'))


@app.route('/myreviews')
def user_reviews():
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

