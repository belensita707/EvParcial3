from flask import Flask, request, render_template_string, session, redirect, url_for, flash
import mysql.connector
import pymysql.cursors
import os
import hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_db_connection():
    db_config = {
        'host': 'mysql-db',  # CAMBIO TÉCNICO: 'mysql-db' para que funcione en Docker
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

        print(password)
        
        
        if "' OR '" in password:
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            # Ejecución directa insegura
            cur = conn.cursor()
            cur.execute(query)
            user = cur.fetchone()
        else:
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            hashed_password = hash_password(password)
            print(password)
            print(hashed_password)
            
            cur = conn.cursor(dictionary=True) 
            cur.execute(query, (username, hashed_password))
            user = cur.fetchone()
            
        cur.close() # Cerramos cursor
        

        print("Consulta SQL generada:", query)

        print (user)
        print(session)
        
        if user:
            session['user_id'] = user['id'] if isinstance(user, dict) else user[0]
            session['role'] = user['role'] if isinstance(user, dict) else user[3]
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

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
    tasks = cur.fetchall() 
    cur.close()

    return render_template_string('''
        <h1>Welcome, user {{ user_id }}!</h1>
        <form action="/add_task" method="post">
            <input type="text" name="task" placeholder="New task"><br>
            <input type="submit" value="Add Task">
        </form>
        <h2>Your Tasks</h2>
        <ul>
        {% for task in tasks %}
            <li>{{ task['tasks'] }} <a href="/delete_task/{{ task['id'] }}">Delete</a></li>
        {% endfor
