from flask import Flask, render_template, request, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "super secret key"

'''home page'''
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('signup.html')
    else:
        return render_template('myreviews.html')
    
@app.route('/login')
def test():
    return render_template('login.html')


'''sign up'''
@app.route('/signup', methods = ['POST'])
def signup():
    render_template('signup.html')
    global username
    username = request.form['username']
    password = request.form['password']
    connection = sqlite3.connect('toast.db')
    cursor = connection.cursor()
    #Mike Rhodes - Stack overflow :skull:
    cursor.execute("SELECT username FROM users WHERE username = '{}'".format(username))
    if cursor.fetchone is not None:
        flash('this username is taken')
        return signup()
    else:
        cursor.execute("INSERT INTO users(username, password) VALUES('{}', '{}')".format(username, password))
        connection.commit()
        session['logged_in'] = True
        return(home())


@app.route('/login-verfication', methods = ['POST'])
def login():
        render_template('login.html')
        password = request.form['password'] 
        global username
        username = request.form['username']
        connection = sqlite3.connect('toast.db')
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = '{}'".format(username))
        key = cursor.fetchone()
        connection.close()
        if key[0] == password:   
            session['logged_in'] = True
            return(user_reviews())
        else:
            return 'wrong password!'

'''shows user reviews'''
@app.route('/myreviews')
def user_reviews():
    if not session.get('logged_in'):
        return render_template('signup.html')
    else:
            connection = sqlite3.connect('toast.db')
            cursor = connection.cursor()
            cursor.execute("SELECT review FROM reviews WHERE username = '{}'".format(username))
            reviews = cursor.fetchall()
            return render_template('myreviews.html', reviews = reviews)

'''shows all reviews'''
@app.route('/reviews')

def show_all_reviews():
    connection = sqlite3.connect('toast.db')
    cursor = connection.cursor()
    cursor.execute('SELECT toast.description, review, username FROM Reviews JOIN Toast ON reviews.toast_id = toast.id JOIN Users ON reviews.user_id = users.id')
    reviews = cursor.fetchall()
    connection.close()
    return  render_template("reviews.html", reviews = reviews)



if __name__ == "__main__":
    app.run(debug = True)