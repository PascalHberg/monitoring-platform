# API-Schutz, Ergebnisse und Tests

## API-Schlüssel

Alle `/api/v1/...`-Endpunkte erwarten einen gemeinsamen Schlüssel im Header `X-API-Key`. Ohne korrekt gesetzte `API_TOKEN`-Umgebungsvariable antworten sie absichtlich mit HTTP 503. Ein fehlender oder falscher Schlüssel ergibt HTTP 401. Die Dashboard-Seite fragt den Schlüssel zur Laufzeit ab und hält ihn nur in `sessionStorage` der aktuellen Browser-Sitzung.

Für Docker Compose:

```bash
export API_TOKEN='replace-with-a-long-random-secret'
docker compose up --build
```

Öffne danach `http://localhost:8000`, gib denselben Schlüssel im Dashboard ein und wähle „Schlüssel verwenden“. Für direkte API-Aufrufe muss der Header mitgeschickt werden:

```bash
curl -H "X-API-Key: $API_TOKEN" http://localhost:8000/api/v1/hosts
```

Nutze die Anwendung nur für Systeme, für deren Prüfung du ausdrücklich autorisiert bist. Für einen Betrieb über ein nicht vertrauenswürdiges Netzwerk sollten zusätzlich HTTPS, ein Secret-Management-System und ein individuelles Nutzer-/Rollenmodell eingesetzt werden. Ein gemeinsamer API-Schlüssel ist eine einfache Basissicherung, keine vollständige Benutzerverwaltung.

## Ergebnisse und Fehler

Prüfresultate enthalten `checked_at` als UTC-Zeitstempel sowie `error_code` und eine verständliche `error`-Meldung. Bei einem Fehler liefert die Compliance-Prüfung `status: ERROR` und keinen irreführenden Score. Ein fehlgeschlagener Ping wird als nicht erreichbar ausgewiesen; ICMP kann auch durch eine Firewall blockiert sein.

## Tests

Die Tests nutzen Python-Standardbibliothek und Mocking, damit keine echten Netzwerkprüfungen ausgeführt werden:

```bash
python -m unittest discover -s tests -v
```
