# Raw benchmark run: 02-baseline

- Thread: `019f8c5b-6e65-7e30-8d5a-232f1cbd1f2d`
- Repository revision: `dbf8381c726f845f332927ad54632fbbe3fea84a`
- Codex model: configured default; thread API did not expose model ID
- Started: 2026-07-23T00:23:50.000Z
- Finished: 2026-07-23T00:31:49.000Z
- Elapsed: 479 seconds

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>BENCHMARK RUN 02. Read-only: do not edit files, commit, or push. Plan a pre-release JSON state-schema change that invalidates transitive descendants when an earlier decision changes. Decide migration policy, validation, rollout order, and recovery. No backward compatibility is required. Success: a testable migration plan that preserves valid decisions and never silently accepts stale descendants.

Baseline method: Stress-test this plan. Ask one decision question at a time and wait for my answer before continuing. Produce a usable plan after resolving every dependent decision. When complete, report counts for questions asked, autonomous decisions, human gates, and reassessments.</input>
</codex_delegation>

## Assistant

Entscheidung 1: Wie behandeln wir bestehende v2-Zustände, deren abhängige Entscheidungen keine prüfbare Parent-Snapshot-Provenienz besitzen?

Meine Empfehlung: v3-Hard-Cutover mit explizitem Migrator. Wurzelentscheidungen bleiben erhalten; bereits ungültige Knoten bleiben ungültig; alle gewählten Knoten mit `dependsOn` werden konservativ auf `invalidated` gesetzt und müssen neu bewertet werden. Danach speichert jede Auswahl die konkreten Abhängigkeitsentscheidungen, gegen die sie validiert wurde. So wird kein möglicherweise veralteter Nachfolger stillschweigend übernommen.

Akzeptierst du diese einmalige konservative Invalidierung bestehender abhängiger Entscheidungen, oder müssen nachweislich gültige v2-Nachfolger durch einen geführten Reassessment-Migrationslauf erhalten bleiben?



## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Accept the v3 hard cutover. Retain a backup until verification passes. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 2: Wie soll v3 die Gültigkeit abhängiger Entscheidungen beweisen?

Meine Empfehlung: Jeder gewählte abhängige Knoten speichert `basedOn` als Abbildung seiner direkten Abhängigkeiten auf deren jeweilige `choice`, zum Beispiel `"basedOn": {"storage": "json"}`. Beim Laden muss exakt gelten: Schlüssel entsprechen `dependsOn`, Werte entsprechen den aktuellen Parent-Entscheidungen, und alle Parents sind gültig. Jede Abweichung ist ein harter Validierungsfehler—niemals automatische Akzeptanz.

Alternative wären Revisionsnummern pro Knoten. Sie sind kompakter, aber weniger nachvollziehbar und zusätzliche Zustandsmechanik.

Akzeptierst du `basedOn` mit den konkreten direkten Parent-Auswahlen als v3-Provenienz?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Accept basedOn with direct parent choices. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 3: Was passiert, wenn v3 beim Laden eine `basedOn`-Abweichung findet—etwa nach manueller JSON-Bearbeitung oder einem abgebrochenen externen Update?

Meine Empfehlung: strikt fehlschlagen und den betroffenen Knoten samt Ursache nennen. Keine automatische Reparatur beim Lesen. Ein separater expliziter Reassessment-/Repair-Schritt invalidiert den Knoten und alle Nachfolger. Reguläre Änderungen über `choose` aktualisieren Parent und Nachfolger atomar in einem Schreibvorgang.

Damit bleibt Validierung nebenwirkungsfrei und stale Entscheidungen werden weder akzeptiert noch unbemerkt verändert.

Akzeptierst du dieses Fail-closed-Verhalten mit expliziter Reparatur?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Accept fail-closed validation and explicit repair. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 4: Soll v3 die frühere Auswahl eines invalidierten Nachfolgers im aktiven Zustand behalten?

Meine Empfehlung: Nein. `choice`, `actor`, `confidence` und `basedOn` werden gelöscht; `status` wird `invalidated`. Die v2-Sicherung bleibt nur für Migrations-Recovery erhalten. Eine zusätzliche `previousChoice`-Historie wäre außerhalb des MVP und könnte versehentlich wie eine gültige Entscheidung behandelt werden.

Akzeptierst du das vollständige Entfernen stale Auswahlwerte aus dem aktiven v3-Zustand?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Yes, fully clear stale selection fields. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 5: Wie soll Migration und Recovery technisch ablaufen?

Meine Empfehlung: `migrate` erstellt zuerst exklusiv `<state>.v2.bak` und überschreibt keine vorhandene Sicherung. Anschließend erzeugt es v3 in einer temporären Datei, validiert diese vollständig und ersetzt erst dann atomar die aktive Datei. Bei jedem Fehler bleibt v2 aktiv. Nach Erfolg bleibt die Sicherung bestehen; Löschung erfolgt bewusst außerhalb des Migrators. Rollback bedeutet: Sicherung zurückkopieren und die letzte v2-Version des Tools verwenden.

Akzeptierst du diesen atomaren Ablauf ohne automatische Backup-Löschung oder automatischen Rollback?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Accept the atomic migration and retained backup. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 6: Soll v3 Abhängigkeitszyklen verbieten?

Meine Empfehlung: Ja. `dependsOn` muss einen gerichteten azyklischen Graphen bilden; die Listenreihenfolge der Knoten bleibt dabei irrelevant. Validierung meldet den konkreten Zyklus. Ohne diese Regel sind „Nachfolger“, Reassessment-Reihenfolge und `basedOn`-Gültigkeit nicht eindeutig.

Akzeptierst du die DAG-Pflicht ohne Zwang, Parent-Knoten im JSON vor ihren Kindern anzuordnen?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Yes, require a DAG and report concrete cycles. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 7: Wann ist `basedOn` Pflicht?

Meine Empfehlung: Für jeden Knoten mit gültiger `choice` zwingend—bei Wurzeln als leeres Objekt `{}`. Knoten ohne `choice` dürfen kein `basedOn` besitzen. Dadurch kann fehlende Provenienz nie als „keine Abhängigkeiten“ durchrutschen, und die Invariante bleibt einheitlich.

Akzeptierst du diese strikte Kopplung von `choice` und `basedOn`?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Yes, require basedOn exactly when choice exists. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 8: Soll ein Parent-Wechsel den gesamten transitiven Teilbaum invalidieren, auch Knoten ohne bisherige Auswahl?

Meine Empfehlung: Ja. Jeder transitive Nachfolger erhält `status: "invalidated"`; vorhandene Auswahlfelder werden gelöscht. Sonst könnten `pending`, `blocked` oder `derived` fälschlich weiterhin als auf dem neuen Pfad gültig erscheinen. Reassessment aktiviert die Knoten anschließend in Abhängigkeitsreihenfolge neu.

Akzeptierst du die Invalidierung aller transitiven Nachfolger unabhängig von deren bisherigem Status?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Yes, invalidate every transitive descendant regardless of prior status. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 9: Darf `repair` Entscheidungen selbst neu treffen?

Meine Empfehlung: Nein. `repair` macht nur den Zustand wieder ladbar: Es findet jeden `basedOn`-Mismatch, invalidiert diese Knoten samt transitiven Nachfolgern und schreibt atomar. Neue Entscheidungen erfolgen danach über den normalen Reassessment-Ablauf, jeweils erst wenn alle direkten Parents gültig gewählt sind.

Akzeptierst du diese Trennung zwischen mechanischer Reparatur und fachlicher Neubewertung?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Yes, repair only invalidates; reassessment makes decisions. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 10: Darf v3 veröffentlicht werden, bevor der native Codex-Fallback dieselben Regeln beherrscht?

Meine Empfehlung: Nein. Python-Backend, native Fallback-Anweisungen, Beispielzustand und Dokumentation wechseln gemeinsam auf v3. Bis alle Pfade dieselben `basedOn`-, DAG-, Invalidierungs- und Fail-closed-Regeln anwenden, bleibt v2 der aktive Stand. Ein gestaffelter Rollout würde denselben Zustand je Backend unterschiedlich behandeln.

Akzeptierst du einen einzigen Paritäts-Gate für beide Backends statt eines Python-first-Rollouts?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Yes, require backend parity before release. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 11: Welche Prüfung schließt Migration und Rollout ab?

Meine Empfehlung: Ein fester End-to-End-Gate mit derselben verzweigten Fixture für beide Backends:

1. v2 migrieren; Backup bytegenau prüfen.
2. Gültige Wurzelentscheidungen bleiben erhalten.
3. Nicht beweisbare abhängige Entscheidungen und deren Nachfolger sind invalidiert.
4. In DAG-Reihenfolge neu entscheiden; `basedOn` wird exakt gesetzt.
5. Frühen Parent ändern; ausschließlich alle transitiven Nachfolger werden invalidiert.
6. JSON manuell stale machen; normales Laden muss scheitern.
7. `repair` invalidiert mechanisch, danach funktionieren Reassessment, Render und Export.
8. Vollständige Testsuite läuft grün.

Erst danach gilt das Backup als entbehrlich und v3 als releasefähig. Akzeptierst du diesen gemeinsamen Release-Gate?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Yes, accept that shared end-to-end release gate. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 12: Soll v3 den bisherigen `assessment.status: "invalidated"`-Marker je Option behalten?

Meine Empfehlung: Nein. Invalidierung gehört ausschließlich zum Knoten über `status: "invalidated"`. Alle Optionen eines invalidierten Knotens sind dadurch unselektierbar. Der doppelte Marker kann auseinanderlaufen und ist bereits nur teilweise validiert. v3 entfernt ihn ohne Kompatibilitätspfad.

Akzeptierst du, den redundanten Option-Level-Status vollständig aus Schema und Logik zu entfernen?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>No. Keep option-level invalidation because current state rules and tests require every affected option assessment to be invalidated. Reassess accordingly, then continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Reassessment 1: Option-Level-Invalidierung bleibt Teil von v3.

Entscheidung 13: Wie verhindern wir Widersprüche zwischen Node- und Option-Status?

Meine Empfehlung: Harte Invariante:

- `node.status == "invalidated"` → jede Option hat `assessment.status == "invalidated"`.
- Jeder andere Node-Status → keine Option darf `assessment.status` enthalten.
- `repair`, Parent-Wechsel und Migration setzen beide Ebenen gemeinsam.
- Reassessment entfernt alle Option-Marker, bevor eine neue Auswahl gespeichert wird.

Akzeptierst du diese strikt gekoppelte Darstellung?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Yes, enforce that strict coupled invariant. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 14: Soll v3 auch Auswahl-, Status- und Actor-Felder als geschlossene Zustandsmatrix validieren?

Meine Empfehlung: Ja:

- Mit `choice`: `basedOn` und `actor` sind Pflicht; Status nur `recommended`, `confirmed` oder `derived`.
- Ohne `choice`: kein `basedOn`, kein `actor`; Status nur `pending` oder `invalidated`.
- `invalidated`: zusätzlich `confidence: null` und alle Option-Assessments invalidiert.
- `pending`: keine Option darf invalidiert sein.
- `actor: human` verlangt `confirmed`; `actor: ai` erlaubt `recommended` oder `derived`.

Akzeptierst du diese Matrix, sodass widersprüchliche Teilzustände fail-closed abgelehnt werden?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Yes, enforce the closed state matrix. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 15: Muss v3 gleichzeitige Schreibprozesse unterstützen?

Meine Empfehlung für den lokalen Pre-Release-MVP: Nein. Alle Mutationen schreiben atomar per Temp-Datei und `os.replace`, aber es gibt keinen Locking-Layer. Der Vertrag ist ein einzelner Writer pro Zustandsdatei; parallele Änderungen sind nicht unterstützt und werden dokumentiert. Plattformübergreifendes Locking würde zusätzliche Mechanik erzeugen.

Akzeptierst du den expliziten Single-Writer-Vertrag, oder muss „nie stale akzeptieren“ auch konkurrierende Prozesse abdecken?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Accept a documented single-writer contract for the local pre-release state file. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 16: Soll `migrate` idempotent sein?

Meine Empfehlung: Nein. Es akzeptiert ausschließlich valide v2-Dateien. v1, v3, unbekannte Versionen oder vorhandenes `<state>.v2.bak` führen vor jeder Änderung zu einem klaren Fehler. Dadurch werden Wiederholungen und versehentliches Überschreiben der Recovery-Sicherung sichtbar.

Akzeptierst du diesen strikt einmaligen v2→v3-Migrationsvertrag?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Yes, migration is strictly one-shot and refuses an existing backup. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 17: Wie behandelt der Migrator v2-Dateien, die der alte Validator akzeptiert, aber bereits inkonsistente Invalidierungsfelder enthalten?

Meine Empfehlung: Nur sicherheitsgerichtet normalisieren. Ein `invalidated`-Knoten wird vollständig bereinigt und alle Option-Marker werden gesetzt; ausgewählte abhängige Knoten werden wie beschlossen invalidiert. Strukturelle Fehler—unbekannte Abhängigkeiten, Zyklen, ungültige Choices oder Assessments—brechen die Migration ab und lassen Original plus Backup unverändert.

Akzeptierst du diese begrenzte Normalisierung statt eines vollständigen Fail bei alten, sicher reparierbaren Statusabweichungen?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>Accept only the limited safety-directed normalization. Continue with the next single decision question.</input>
</codex_delegation>

## Assistant

Entscheidung 18: Wann darf die v2-Sicherung tatsächlich zurückgespielt werden?

Meine Empfehlung: Nur wenn Migration oder Verifikation fehlschlägt, bevor irgendeine neue v3-Entscheidung gespeichert wurde. Sobald v3 fachlich weiterbearbeitet wurde, würde ein Restore diese Arbeit verlieren; dann bleibt v3 aktiv und `repair` ist der Recovery-Pfad. Das Backup bleibt trotzdem bis zum bestandenen Release-Gate erhalten.

Akzeptierst du diese klare Rollback-Grenze?

## User

<codex_delegation>
  <source_thread_id>019f8c04-606a-70c2-bd37-4d1f424def46</source_thread_id>
  <input>The fixed answer key covers no further preference. Use your best judgment for all remaining reversible details, note this fallback, and now produce the final usable plan with counts for questions asked, autonomous decisions, human gates, and reassessments.</input>
</codex_delegation>

## Assistant

## Finaler v3-Plan

Ziel: Jede gültige Auswahl beweist mit `basedOn`, auf welchen direkten Parent-Auswahlen sie beruht. Stale oder widersprüchliche Nachfolger werden nie still akzeptiert.

### 1. Schema v3

```json
{
  "version": 3,
  "nodes": [{
    "id": "child",
    "dependsOn": ["parent"],
    "choice": "selected-option",
    "basedOn": {
      "parent": "parent-option"
    }
  }]
}
```

Regeln:

- `dependsOn` bildet einen DAG; konkrete Zyklen werden gemeldet.
- Mit `choice` ist `basedOn` Pflicht, bei Wurzeln `{}`.
- Ohne `choice` darf `basedOn` nicht existieren.
- `basedOn` enthält exakt alle direkten Parents und deren aktuelle Choices.
- Alle Parents müssen gültig gewählt sein.
- Jede Abweichung führt beim Laden fail-closed zum Fehler.

Geschlossene Zustandsmatrix:

- Mit `choice`: `actor` erforderlich; Status nur `recommended`, `confirmed` oder `derived`.
- Ohne `choice`: kein `actor`, kein `basedOn`; Status nur `pending` oder `invalidated`.
- `actor: human` verlangt `confirmed`.
- `actor: ai` erlaubt `recommended` oder `derived`.
- `invalidated` verlangt `confidence: null` und `assessment.status: "invalidated"` auf jeder Option.
- Bei allen anderen Node-Statuswerten darf kein Option-Assessment einen `status` enthalten.

### 2. Zentrale Invalidierung

Eine vorhandene gemeinsame Funktion invalidiert einen Knoten vollständig:

- `choice`, `actor`, `confidence` und `basedOn` entfernen beziehungsweise leeren.
- Node-Status auf `invalidated` setzen.
- Grund auf erforderliches Reassessment setzen.
- Jede Option mit `assessment.status: "invalidated"` markieren.

Ein Parent-Wechsel wendet dies auf sämtliche transitiven Nachfolger an, unabhängig von deren vorherigem Status. Unabhängige Knoten bleiben unverändert.

Reassessment erfolgt in DAG-Reihenfolge über den bestehenden Replace-/Entscheidungsfluss. Es ist nur erlaubt, wenn alle direkten Parents gültige Choices besitzen. Dabei werden alle Option-Level-Marker entfernt und `basedOn` neu erzeugt.

### 3. Validierung und Repair

Validierung läuft in dieser Reihenfolge:

1. Version und Grundstruktur.
2. eindeutige IDs, bekannte Abhängigkeiten und gültige Optionsreferenzen.
3. DAG-Prüfung mit konkreter Zyklusausgabe.
4. geschlossene Zustandsmatrix.
5. gekoppelte Node-/Option-Invalidierung.
6. exakte `basedOn`-Provenienz.

Normales Laden verändert niemals Dateien.

`repair`:

- liest v3 mit struktureller Validierung, aber toleriert ausschließlich reparierbare Provenienz-/Statusabweichungen;
- findet alle `basedOn`-Mismatch-Knoten;
- invalidiert diese und sämtliche transitiven Nachfolger;
- trifft keine neuen Entscheidungen;
- schreibt erst nach vollständiger abschließender Validierung atomar.

Strukturelle Fehler wie Zyklen oder unbekannte Referenzen bleiben harte Fehler.

### 4. Einmalige v2→v3-Migration

Neuer expliziter `migrate`-Befehl:

1. Akzeptiert ausschließlich eine valide v2-Datei.
2. Verweigert v1, v3, unbekannte Versionen und vorhandenes `<state>.v2.bak`.
3. Erstellt `<state>.v2.bak` bytegenau und exklusiv.
4. Baut v3 in einer temporären Datei.
5. Bewahrt gültige Root-Entscheidungen und ergänzt `basedOn: {}`.
6. Bewahrt ungewählte, weiterhin erreichbare Pending-Knoten.
7. Normalisiert bereits invalidierte Knoten sicherheitsgerichtet.
8. Invalidiert jede gewählte abhängige v2-Entscheidung, deren Provenienz nicht beweisbar ist, plus deren transitive Nachfolger.
9. Validiert das vollständige v3-Ergebnis.
10. Ersetzt erst danach die aktive Datei atomar mit `os.replace`.

Bei Fehlern bleibt v2 aktiv. Die Sicherung wird nie automatisch gelöscht.

### 5. Schreibverhalten

Alle mutierenden Befehle verwenden Temp-Datei plus `os.replace`.

Dokumentierter Vertrag: genau ein Writer pro Zustandsdatei. Prozessübergreifendes Locking bleibt außerhalb des lokalen Pre-Release-MVP.

### 6. Tests

In `scripts/test_decision_state.py` mindestens folgende Fälle ergänzen:

- gültige Root- und Child-`basedOn`-Werte;
- fehlende, zusätzliche und falsche Parent-Snapshots;
- Parent ohne gültige Choice;
- direkte und längere Zyklen mit konkretem Pfad;
- jede erlaubte und verbotene Kombination der Zustandsmatrix;
- widersprüchliche Node-/Option-Invalidierung;
- Parent-Wechsel invalidiert alle und nur transitive Nachfolger;
- Invalidierung löscht sämtliche stale Auswahlfelder;
- Reassessment setzt neue Provenienz und entfernt Option-Marker;
- normales Laden repariert nichts;
- `repair` invalidiert, entscheidet aber nichts;
- v2-Migration bewahrt Root-Entscheidungen;
- v2-Migration invalidiert nicht beweisbare Nachfolger;
- Backup ist bytegleich;
- vorhandenes Backup und falsche Versionen werden verweigert;
- Migrationsfehler verändert die aktive Datei nicht;
- Render und Export funktionieren mit gültigem v3 und verweigern stale v3.

Abschlussprüfung:

```bash
python3 scripts/test_decision_state.py
```

### 7. Rollout-Reihenfolge

1. Tests für v3-Invarianten zunächst fehlschlagend festlegen.
2. DAG-, Zustandsmatrix- und Provenienzvalidierung implementieren.
3. zentrale Invalidierung und atomare Writes ergänzen.
4. `migrate` und `repair` implementieren.
5. versioniertes Beispiel auf v3 migrieren.
6. `SKILL.md` und nativen Codex-Fallback auf exakt dieselben Regeln umstellen.
7. README und `CHANGELOG.md` unter `Unreleased` aktualisieren.
8. gemeinsamen End-to-End-Gate für Python-Backend und nativen Fallback ausführen.
9. Erst bei vollständiger Parität v3 veröffentlichen.

Kein Python-first-Rollout; v2 bleibt aktiv, bis beide Backends bereit sind.

### 8. End-to-End-Release-Gate

Mit derselben verzweigten Fixture in beiden Backends:

1. v2 migrieren und Backup bytegenau prüfen.
2. Root-Entscheidungen als erhalten nachweisen.
3. nicht beweisbare Nachfolger als invalidiert nachweisen.
4. Pfad in DAG-Reihenfolge neu entscheiden.
5. frühe Parent-Choice ändern und exakte transitive Invalidierung prüfen.
6. `basedOn` manuell stale machen und Fail-closed-Laden prüfen.
7. `repair`, Reassessment, Render und Export prüfen.
8. vollständige Testsuite ausführen.

### 9. Recovery

Autonom festgelegt, weil der Answer Key keine weitere Präferenz enthält:

- Rollback auf v2 nur bei fehlgeschlagener Migration oder Verifikation, bevor neue v3-Entscheidungen gespeichert wurden.
- Dafür Backup zurückkopieren und die letzte v2-Toolversion verwenden.
- Nach neuer v3-Arbeit bleibt v3 aktiv; Recovery erfolgt über `repair`, damit keine neue Arbeit verloren geht.
- Backup erst nach bestandenem gemeinsamen Release-Gate manuell entfernen.
- Keine Migrationshistorie oder `previousChoice` im aktiven Schema.

## Benchmark-Zählung

- Fragen gestellt: **18**
- Menschliche Gates entschieden: **17**
- Autonome Entscheidungen: **4**
  - Rollback-Grenze nach ausgeschöpftem Answer Key
  - keine zusätzliche Migrationsmetadaten-Historie
  - bestehender Replace-Fluss für Reassessment statt neuer Abstraktion
  - keine automatische Backup-Löschung
- Reassessments: **1**
  - Option-Level-Invalidierung nach Ablehnung der ursprünglichen Entfernung neu eingeplant

Keine Dateien geändert, committed oder gepusht.



