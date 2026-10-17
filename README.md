# hftm IT-Security Labs 

## Allgemeine Voraussetzungen

Bevor du mit den Labs starten kannst, müssen folgende Tools auf deinem Rechner installiert sein:
1. **Docker** (Stelle bei Windows sicher, dass das WSL2-Backend aktiviert ist): [https://www.docker.com/](https://www.docker.com/)
2. **Git**
3. Eine IDE deiner Wahl
4. Git-Repo klonen:

```
# 1. Repository klonen (via HTTPS oder SSH)
git clone https://github.com/dobaumann/IN267_IT-Security.git

# 2. In das geklonte Verzeichnis wechseln (Extrem wichtig für das Volume-Mapping!)
cd IN267_IT-Security   
```

---

## Lab Workflow

1. Öffne dein Terminal im Hauptverzeichnis dieses Repositories (`git/`).
2. Hole dir die neuesten Aufgaben und Updates:
```bash
   git pull
```
3. Jedes Lab ist in einem separaten Unterordner abgelegt. **Dort findest du im README.md auch die Aufgabenbeschreibung.**

4. Starte das gewünschte Lab mithilfe des Docker-Compose-Profils (siehe Tabelle unten).
```bash
   docker compose --profile <labXY> up --build
```
5. Im Normalfall wird das Lab jetzt unter **[http://localhost:5000](http://localhost:5000)** erreichbar sein. Solltest du bereits selbst einen Service unter Port 5000 betreiben, kannst du das Port-Mapping in docker-compose.yaml anpassen.

---

## Das 3-Schritte-Prinzip pro Aufgabe

Jedes Lab ist nach demselben didaktischen Prinzip aufgebaut:

1. **Lab starten:** Starte den Container über den entsprechenden Profil-Befehl im Terminal.
2. **Hacking (Offensive):** Analysiere die Anwendung, finde die Schwachstelle und schreibe ein automatisiertes Skript (z. B. in Python), um die **FLAG** (den Erfolgs-Code) zu extrahieren.
3. **Fixing (Defensive):** Wechsle die Seiten. Optimiere den Quellcode (oft `main.py`) im jeweiligen Unterordner direkt auf deinem Rechner, um die Schwachstelle dauerhaft zu schliessen. Dein Fix wird live in den Container übertragen und bleibt persistent auf deiner Festplatte gespeichert.
