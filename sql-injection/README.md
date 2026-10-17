# IT-Security Lab: SQL-Injection

In diesem Lab lernst du, wie Angreifer fehlerhafte SQL-Abfragen manipulieren, um Authentifizierungen zu umgehen, fremde Datenbanktabellen auszulesen und Daten über Blind-Techniken zeichenweise zu extrahieren. Anschliessend schlüpfst du in die Rolle des Entwicklers und sicherst die Anwendung gegen diese Angriffe ab.

Theorie und Erklärungen findest du auf der OWASP-Website: https://community.owasp.org/attacks/SQL_Injection

## 1. Lab starten

Öffne dein Terminal im Hauptverzeichnis des Repositories (im Ordner `git/`) und führe folgenden Befehl aus:


```
docker compose --profile sql-injection up --build
```

Rufe danach die Webseite in deinem Browser auf und sieh dir die Website an: **[http://localhost:5001](http://localhost:5001/)**

  
## 2. Angreifen (Offensive)

Die Webapplikation der **Faust Electronics GmbH** leidet an mehreren Stellen unter ungesäuberten Benutzereingaben, die direkt per String-Verkettung in SQL-Befehle eingebunden werden.

### a. Level 1: Authentication Bypass

Das Admin-Portal (`/level1`) simuliert einen Admin-Zugang und überprüft Benutzername und Passwort über eine relationale Datenbank.

**Szenario:** Du bist ein Angreifer und kennst das Passwort des Benutzers `admin` nicht. Dein Ziel ist es, dich als admin in den Server einzuloggen und das Flag auszulesen, ohne das Passwort eingeben zu müssen.

**Aufgabe:**

1. Analysiere das Anmeldeformular und manipuliere die Eingabe im Feld **Benutzername** so, dass die SQL-Bedingung für das Passwort ignoriert wird.

2. Verschaffe dir als `admin` Zugang zum System und lies das Flag aus.

_Hinweis:_ Überlege, mit welchem Zeichen ein String in SQL abgeschlossen wird und wie SQL-Kommentare (`--`) funktionieren. Die OWASP-Website hat gute Erklärungen dazu

**Bonusaufgabe**: Kreative könnten jetzt auf die Idee kommen, der Eingabe noch ein INSERT-Statement hinzuzufügen und sich einfach einen eigenen Admin-Account zu erstellen. Findest du heraus, wieso dies bei diesem Server nicht funktioniert? 
*Hinweis*: Pythons query.execute() vs. query.executeScript()

  
### b. Level 2: UNION-Based Data Extraction

Im simulierten Mitarbeiter-Verzeichnis (`/level2`) können Informationen (Abteilung, E-Mail) zu Angestellten nach ihrem Namen in einer Datenbanktabelle gesucht werden. Dazu wird folgender SQL-Befehl verwendet:

```query = f"SELECT id, name, department, email FROM employees WHERE name LIKE '%{query_param}%'" ```

**Szenario:** 
Du bist ein Angreifer und willst die Suche missbrauchen, um Datensätze aus ganz anderen Tabellen auszulesen. Dein Ziel ist es, die "geheime" Tabelle zu finden und das Flag daraus auszulesen. Verwende dazu den UNION-Operator von SQL, um Informationen aus der geheimen Tabelle auszulesen.

SQL UNION
```
SELECT id, name, department FROM employees 
UNION 
SELECT id, flag, 3, 4 FROM <geheime_tabelle>
```
 
**Aufgabe:**

1. Ermittle mithilfe von `ORDER BY` die exakte Spaltenanzahl der ursprünglichen Abfrage. Das brauchst du, um eine korrekte UNION-Abfrage aufzubauen (die linke und rechte Tabelle müssen in der Abfrage die gleiche Anzahl Spalten haben).

2. Nutze einen `UNION SELECT`-Angriff, um über die Metatabelle `sqlite_master` die Namen aller Tabellen der Datenbank herauszufinden. Die sqlite_master Tabelle speichert die Namen aller Tabellen.

3. Lies den Inhalt der geheimen Tabelle aus, um die Flagge zu finden.

Hinweis: Beachte  das schliessende `%` der ursprünglichen `LIKE`-Suche des SQL-Strings auf dem Server!
Hinweis: Die Tabelle licences enthält ein Flag für die nächste Aufgabe. Sie ist nicht das Ziel dieses Angriffs!


### c. Level 3: Boolean-Based Blind SQL-Injection

Die simulierte Lizenz-Prüfung (`/level3`) besitzt eine API-Schnittstelle (`/level3/api/check-license?key=...`), die von externen Clients aufgerufen werden kann und zurückgibt, ob eine Lizenz gültig ist oder nicht.

Der Server gibt weder Fehlermeldungen noch Inhalte aus der Datenbank zurück – lediglich ein boolesches Feedback:

- Lizenz gültig: `{"status": "success", "message": "Lizenz gültig."}`
- Lizenz ungültig: `{"status": "error", "message": "Lizenz ungültig."}`

Die Flagge ist als Lizenzschlüssel in der Tabelle `licenses` hinterlegt.

**Szenario**: Du bist ein Angreifer und willst jetzt diese API missbrauchen. Dein Ziel ist es, eine gültige Lizenz herauszufinden. Benutze dazu die Boolean-Based Blind SQL-Injection (die OR und AND Operatoren in SQL), um den Lizenzschlüssel zu Zeichen für Zeichen zu erraten.

**Aufgabe:**

1. Teste manuell in der URL oder via Browser, wie die API auf wahre Aussagen (`' OR 1=1 --`) und falsche Aussagen (`' OR 1=2 --`) reagiert.

2. Schreibe ein Python-Skript (unter Verwendung der Bibliothek `requests`), welches die SQLite-Funktion `SUBSTR()` nutzt, um den Lizenzschlüssel Zeichen für Zeichen automatisiert abzufragen.


_Hinweis:_ Beginne dein Skript mit einem Zeichensatz wie `string.ascii_letters + string.digits + "{}_-!"` und prüfe pro Position, welches Zeichen ein `status: success` liefert.

  


## 3. Verteidigen (Defensive)

Wechsle nun in die Rolle des Softwareentwicklers der Faust Electronics GmbH.

String-Verkettungen und dynamisch zusammengesetzte Abfragen sind die Hauptursache für SQL-Injections. Das manuelle Filtern von Zeichen wie `'` oder `--` (Blacklisting) ist notorisch fehleranfällig und unvollständig. Die einzig zuverlässige Abwehrmassnahme sind **parametrisierte Statements (Prepared Statements)**.

**Aufgabe:**

1. Öffne die Datei `sql-injection/main.py` in deinem Editor.
    
2. Behebe die Sicherheitslücken in allen drei Endpoints (`/level1`, `/level2`, `/level3/api/check-license`), indem du die Abfragen auf parametrisierte SQL-Befehle umstellst.

    _Beispiel für Prepared Statements mit SQLite in Python:_

    Python
    ```
    # Unsicher:
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    
    # Sicher (Parameter werden als Tupel übergeben):
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    ```
    
3. Starte den Container neu oder überprüfe direkt im Browser, ob:

    - Die reguläre Nutzung (z. B. legitimer Login mit `admin` / `Sup3rS3cr3tP4ssw0rd!`) weiterhin einwandfrei funktioniert.
        
    - Deine Angriffe aus Abschnitt 2 zuverlässig abgewehrt werden.

Teile deinen bereinigten Code auf dem Forum in Moodle.
 

_Hinweis:_ Der [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) bietet eine Übersicht über sichere Implementierungsmuster.

  

## 4. Bonus (nicht prüfungsrelevant, für Begeisterte)

In professionellen Penetrationstests werden SQL-Injections selten rein manuell ausgebeutet. Das Tool **sqlmap** ist das Standardwerkzeug zur automatisierten Erkennung und Ausnutzung von SQL-Injections.

1. Installiere `sqlmap` lokal auf deinem Rechner (z. B. via Paketmanager oder [GitHub](https://github.com/sqlmapproject/sqlmap)).

2. Wende `sqlmap` auf das zweite Level (Mitarbeitersuche) an:

	``` sqlmap -u "http://localhost:5001/level2?q=Alice" --batch```

3. Lass dir von `sqlmap` das gesamte Datenbankschema und die Tabelleninhalte extrahieren:

    ```sqlmap -u "http://localhost:5001/level2?q=Alice" --dump ```

4. Versuche, ob `sqlmap` auch die Blind-SQL-Injection in Level 3 vollautomatisch knacken kann.

5. Vergleiche die Geschwindigkeit deines eigenen Python-Skripts mit der Optimierung (Bisection / Binary Search) von `sqlmap`.
 
!! Die Verwendung von SQLMap für Angriffe auf unberechtigte Systeme ist strafbar !!