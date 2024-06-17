from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3


app = Flask(__name__)
app.secret_key = "super secret key"

'''home page'''
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('user_reviews'))
    else:
        return redirect(url_for('signup'))

def home():
    if session['username'] is not None:
        return redirect(url_for('signup'))
    # elif Flag == True:
    #     text = 'this username is taken'
    #     return render_template('signup.html', text = text)
    else:
        return redirect(url_for('user_reviews'))
    


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method =='GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = sqlite3.connect('toast.db')
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = '{}'".format(username))
        key = cursor.fetchone()
        connection.close()
        if key[0] == password:
            session['username'] = username 
            return redirect(url_for('user_reviews'))
        elif key is None:
            error_message = 'incorrect username'
            return render_template('login.html', error_message = error_message)
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
        connection = sqlite3.connect('toast.db')
        cursor = connection.cursor()
        #Mike Rhodes - Stack overflow :skull: verfication that username is not taken already
        cursor.execute("SELECT username FROM users WHERE username = '{}'".format(username))
        if cursor.fetchone() is not None:
            error_message = 'username is taken'
            return render_template('signup.html', error_message = error_message)
        else:
            cursor.execute("INSERT INTO users(username, password) VALUES('{}', '{}')".format(username, password))
            connection.commit()
            session['logged_in'] = True
            return redirect(url_for('index'))
        

@app.route('/create_review', methods = ['GET', 'POST'])
def create_review():
    if session['username'] is None:
        return redirect(url_for('login'))
    elif request.method == 'GET':
        connection = sqlite3.connect('toast.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Toast')
        toasts = cursor.fetchall()
        return render_template('create_reviews.html', toasts=toasts)
    elif request.method == 'POST':
        toast_id = request.form['value']
        toast_review = request.form['review']
        username = session['username']
        connection = sqlite3.connect('toast.db')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users(user_id, review, toast_id) VALUES('{}', '{}')".format(toast_id, toast_review))



@app.route('/logout')
def logout():
    session['username'] = None
    return redirect(url_for('index'))





#things that are fine aka don;t need request.['something']

'''shows user reviews'''
@app.route('/my-reviews')
def user_reviews():
    if session["username"] is None:
        return render_template('signup.html')
    else:
        username = session["username"]
        connection = sqlite3.connect('toast.db')
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = '{}'".format(username))
        user_id = cursor.fetchone()[0]
        cursor.execute("SELECT review FROM reviews WHERE user_id = '{}'".format(user_id))
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
    return render_template("reviews.html", reviews = reviews)

# def database_command():
#     connection = sqlite3.connect('toast.db')
#     cursor = connection.cursor()
#     cursor.execute('SELECT toast.description, review, username FROM Reviews JOIN Toast ON reviews.toast_id = toast.id JOIN Users ON reviews.user_id = users.id')
#     reviews = cursor.fetchall()
#     connection.close()



if __name__ == "__main__":
    app.run(debug = True)