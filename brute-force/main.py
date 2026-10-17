# Aufgabe 3: Verteidigungskonzept
# IP-basiertes Rate Limiting mit temporärer Sperre nach fünf fehlgeschlagenen Login-Versuchen


import hashlib
import time
from flask import Flask, request, render_template

app = Flask(__name__)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# Gehashte Passwörter
USER_DATABASE = {
    'admin1': '044f07d3e9f586bffda43c444322142ff313fc6f044c5b9ae74db00ab360f706',
    'admin2': 'a1d8529ac580b2e643526d7fda61bd8e0aa759d64092ad7886129c8eef3cc898'
}


# Speichert die Anzahl Fehlversuche pro IP-Adresse
FAILED_ATTEMPTS = {}

# Speichert, bis wann eine IP gesperrt ist
BLOCKED_IPS = {}

# Nach wie vielen Fehlversuchen wird gesperrt?
MAX_ATTEMPTS = 5

# Sperrdauer in Sekunden
BLOCK_TIME = 30


@app.route('/', methods=['GET', 'POST'])
def login():
    message = None

    if request.method == 'POST':

        # IP-Adresse des Clients auslesen
        client_ip = request.remote_addr

        current_time = time.time()


        # Prüfen, ob die IP aktuell gesperrt ist
        if client_ip in BLOCKED_IPS:

            blocked_until = BLOCKED_IPS[client_ip]

            if current_time < blocked_until:
                remaining_time = int(blocked_until - current_time)

                return (
                    f"Zu viele Fehlversuche. "
                    f"Bitte noch {remaining_time} Sekunden warten.",
                    429
                )

            else:
                # Sperre ist abgelaufen
                del BLOCKED_IPS[client_ip]
                FAILED_ATTEMPTS[client_ip] = 0


        username = request.form.get('username')
        password = request.form.get('password')


        # Login erfolgreich
        if USER_DATABASE.get(username) == hash_password(password):

            # Fehlversuche dieser IP zurücksetzen
            FAILED_ATTEMPTS[client_ip] = 0

            return (
                f"<h1>Herzlichen Glückwunsch! "
                f"Zugriff für {username} erfolgreich gewährt.</h1>"
            )


        # Login fehlgeschlagen
        else:

            # Falls IP noch nicht existiert, bei 0 starten
            if client_ip not in FAILED_ATTEMPTS:
                FAILED_ATTEMPTS[client_ip] = 0

            # Fehlversuch erhöhen
            FAILED_ATTEMPTS[client_ip] += 1

            print(
                f"Fehlversuch von {client_ip}: "
                f"{FAILED_ATTEMPTS[client_ip]}"
            )


            # Prüfen, ob maximale Anzahl erreicht wurde
            if FAILED_ATTEMPTS[client_ip] >= MAX_ATTEMPTS:

                BLOCKED_IPS[client_ip] = current_time + BLOCK_TIME

                return (
                    "Zu viele Fehlversuche. "
                    "IP wurde für 30 Sekunden gesperrt.",
                    429
                )


            message = "Ungültige Anmeldedaten. Bitte versuchen Sie es erneut."

            return render_template(
                'login.html',
                message=message
            ), 401


    return render_template('login.html', message=message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)