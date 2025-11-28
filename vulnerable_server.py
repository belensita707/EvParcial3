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
            # Bloque con mala implementación a propósito
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
    conn.close()

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
        {% endfor %}
        </ul>
    ''', user_id=user_id, tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = request.form['task']
    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()
    # Vulnerable a inserción si no se valida, aunque usa %s aquí, el diseño general es débil
    cur.execute("INSERT INTO tasks (user_id, tasks) VALUES (%s, %s)", (user_id, task))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return 'Welcome to the admin panel!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
