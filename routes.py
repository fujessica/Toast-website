from flask import Flask, render_template
import sqlite3


app = Flask(__name__)

@app.route('/')

@app.route('/home')


@app.route('/signup')
def create_user():
    return ":D"


@app.route('/login')
def login():
    return "hallo"


@app.route('/reviews')
def show_reviews():
    return "amongus"




if __name__ == "__main__":
    app.run(debug = True)

