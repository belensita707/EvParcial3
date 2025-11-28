from flask import Flask, request, render_template_string, session, redirect, url_for
import mysql.connector
import os
import hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_db_connection():
    db_config = {
        'host': 'mysql-db',
        'user': 'root',
        'password': '',
        'database': 'prueba'
    }
    conn = mysql.connector.connect(**db_config)
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    return 'Welcome to the Task Manager Application!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()

    
        if "' OR '" in password:
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            cur = conn.cursor()
            cur.execute(query)
            user = cur.fetchone()
        else:
            # Aunque esta parte parece segura, el diseño general es débil
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            hashed_password = hash_password(password)
            cur = conn.cursor()
            cur.execute(query, (username, hashed_password))
            user = cur.fetchone()
            
        cur.close()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['role'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials!'
            
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
