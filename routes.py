from flask import Flask, render_template
import sqlite3


app = Flask(__name__)

@app.route('/')

@app.route('/home')
def home():
    connection = sqlite3.connect('toast.db')
    cursor = connection.cursor()
    cursor.execute('SELECT toast.description, review, username FROM Reviews JOIN Toast ON reviews.toast_id = toast.id JOIN Users ON reviews.user_id = users.id')
    reviews = cursor.fetchall()
    for item in reviews:
        return (f"{item[0]:<25}{item[1]:<45}{item[2]:<20}")


@app.route('/signup')
def create_user():
    return 'among'


@app.route('/login')
def login():
    return "hallo"


@app.route('/reviews')
def show_reviews():
    return "amongus"




if __name__ == "__main__":
    app.run(debug = True)

