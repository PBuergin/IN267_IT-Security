import sqlite3
import os
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)
DATABASE_PATH = 'sqli.db'

def init_db():
    """Initialisiert die Datenbank bei jedem Start neu, damit die Studenten immer einen sauberen Zustand haben."""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # --- LEVEL 1: Auth Bypass ---
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'Sup3rS3cr3tP4ssw0rd!')")

    # --- LEVEL 2: UNION-based ---
    cursor.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, department TEXT, email TEXT)')
    cursor.execute("INSERT INTO employees (name, department, email) VALUES ('Dr. Alice Smith', 'R&D', 'a.smith@faust-electronics.local')")
    cursor.execute("INSERT INTO employees (name, department, email) VALUES ('Bob Jones', 'HR', 'b.jones@faust-electronics.local')")
    cursor.execute("INSERT INTO employees (name, department, email) VALUES ('Eve Hacker', 'IT', 'e.hacker@faust-electronics.local')")
    
    # Geheime Tabelle, die über UNION ausgelesen werden soll
    cursor.execute('CREATE TABLE flags_internal (id INTEGER PRIMARY KEY, flag_name TEXT, flag_value TEXT)')
    cursor.execute("INSERT INTO flags_internal (flag_name, flag_value) VALUES ('UNION_FLAG', 'FLAG{Un10n_M4st3r_2026}')")

    # --- LEVEL 3: Blind SQLi ---
    cursor.execute('CREATE TABLE licenses (id INTEGER PRIMARY KEY, key TEXT, valid INTEGER)')
    # Die Flagge IST der Lizenzschlüssel. Studenten müssen ihn Zeichen für Zeichen auslesen.
    cursor.execute("INSERT INTO licenses (key, valid) VALUES ('FLAG{Bl1nd_SQL1_N1nj4}', 1)")

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Start-Seite / Navigation
@app.route('/')
def index():
    return render_template('index.html')

# --- LEVEL 1: Auth Bypass ---
@app.route('/level1', methods=['GET', 'POST'])
def level1():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # VULNERABLE: Direkte String-Konkatenation
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"[Level 1] Executing Query: {query}")
        
        conn = get_db()
        cursor = conn.cursor()
        try:
            user = cursor.execute(query).fetchone()
            if user:
                return f"<h1>Willkommen im Admin-Panel, {user['username']}!</h1><p>Level 1 bestanden. Flagge: FLAG{{Auth_Byp4ss_Succ3ss}}</p>"
            else:
                message = "Ungültige Anmeldedaten. Bitte versuchen Sie es erneut."
        except sqlite3.Error as e:
            message = f"Datenbankfehler: {e}"
            
    return render_template('level1.html', message=message)

# --- LEVEL 2: UNION-based SQLi ---
@app.route('/level2', methods=['GET'])
def level2():
    query_param = request.args.get('q', '')
    results = None
    error_msg = None
    
    if query_param:
        # VULNERABLE: String-Konkatenation
        query = f"SELECT id, name, department, email FROM employees WHERE name LIKE '%{query_param}%'"
        print(f"[Level 2] Executing Query: {query}")
        
        conn = get_db()
        cursor = conn.cursor()
        try:
            results = cursor.execute(query).fetchall()
        except sqlite3.Error as e:
            # Wichtig für Lernzwecke: Fehler dem User anzeigen!
            error_msg = f"SQL Fehler: {e}"
            
    return render_template('level2.html', results=results, query=query_param, error=error_msg)

# --- LEVEL 3: Blind SQLi ---
@app.route('/level3/api/check-license', methods=['GET'])
def level3_api():
    license_key = request.args.get('key', '')
    
    # VULNERABLE: Blind SQLi. Keine Datenausgabe, keine Fehlerausgabe. Nur True/False.
    query = f"SELECT 1 FROM licenses WHERE key = '{license_key}' AND valid = 1"
    print(f"[Level 3] Executing API Query: {query}")
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        match = cursor.execute(query).fetchone()
        if match:
            return jsonify({"status": "success", "message": "Lizenz gültig."})
        else:
            return jsonify({"status": "error", "message": "Lizenz ungültig."})
    except sqlite3.Error:
        # Fehler werden absichtlich unterdrückt!
        return jsonify({"status": "error", "message": "Lizenz ungültig."})

@app.route('/level3')
def level3_ui():
    return render_template('level3.html')

if __name__ == '__main__':
    init_db()
    print("Datenbank initialisiert.")
    app.run(host='0.0.0.0', port=5000, debug=True)