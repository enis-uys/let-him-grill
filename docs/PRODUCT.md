# Produktkonzept: Let Him Grill

## Problem

Grill-with-Docs-Workflows gehen bewusst Schritt für Schritt vor und erwarten bei
vielen Fragen eine unmittelbare menschliche Antwort. Das liefert Kontrolle,
unterbricht aber auch bei reversiblen oder klar empfehlbaren Entscheidungen den
Arbeitsfluss.

## Ziel

Ein vorgeschalteter Orchestrator soll mehrere Entscheidungsschritte selbstständig
bearbeiten. Er empfiehlt und wählt risikoarme Optionen, dokumentiert Alternativen
und hält erst an, wenn eine menschliche Entscheidung den weiteren Verlauf
wesentlich beeinflusst.

Der Mensch soll den bisherigen Pfad in einem Entscheidungsbaum sehen, frühere
Entscheidungen ändern und den davon abhängigen Teilbaum neu berechnen lassen
können.

## Kernablauf

1. Bestehenden Grill-with-Docs-Kontext, relevante Projektdokumentation und Code
   untersuchen.
2. Nächste Frage samt Optionen und Abhängigkeiten bestimmen.
3. Frage nach Entscheidungstyp klassifizieren.
4. Bei automatisierbaren Fragen eine Empfehlung wählen und begründen.
5. Bis zum nächsten menschlichen Entscheidungspunkt weiterarbeiten.
6. Aktiven Pfad, Alternativen und Begründungen im Baum anzeigen.
7. Nach Änderung einer früheren Entscheidung nur deren abhängigen Teilbaum
   verwerfen und neu berechnen.
8. Nach menschlicher Freigabe fortfahren.

## Betriebsarten

- `kompakt`: gleicher autonomer Ablauf und gleiche Human-Gates, aber Textausgabe;
  Zustand und Visualisierung entstehen nur bei Verzweigungen, Rücksprüngen oder
  auf Wunsch.
- `visuell`: alle Entscheidungen werden in JSON persistiert und an Human-Gates
  sowie nach Änderungen als interaktiver Baum dargestellt.
- `auto`: Codex wählt `kompakt` für kurze lineare und `visuell` für verzweigte
  oder später änderbare Entscheidungsfolgen. Der Nutzer kann jederzeit wechseln.

## Entscheidungstypen

- `auto`: KI darf selbst wählen und fortfahren.
- `review`: KI wählt vorläufig; Mensch kann die Wahl später ändern.
- `human`: Workflow hält vor der Entscheidung an.
- `derived`: Ergebnis folgt aus bereits getroffenen Entscheidungen.
- `blocked`: Notwendige Fakten fehlen; der Workflow fordert nur diese an.

Eine Frage braucht eine menschliche Entscheidung, wenn sie mindestens einen
dieser Bereiche wesentlich verändert:

- Produktziel oder Nutzergruppe
- Architektur oder langfristige Wartung
- irreversible oder schwer rückgängig zu machende Folgen
- Sicherheit, Datenschutz oder Berechtigungen
- externe Kosten, Anbieterbindung oder Betrieb
- widersprüchliche Anforderungen ohne klaren Default
- persönliche, geschäftliche oder gestalterische Präferenz

Reversible, risikoarme und aus Projektkontext klar ableitbare Entscheidungen
sollen nicht unnötig blockieren.

## Daten je Entscheidung

Mindestens erforderlich:

```json
{
  "id": "storage",
  "question": "Wie wird der Zustand gespeichert?",
  "type": "review",
  "choice": "local-json",
  "options": [{
    "id": "local-json",
    "label": "Local JSON",
    "assessment": {
      "triage": "recommended",
      "reason": "Kein Dienst erforderlich.",
      "confidence": 0.94,
      "reversible": true,
      "effort": "low",
      "risk": "low",
      "impact": "Zustand bleibt lokal.",
      "preferredWhen": "Ein Workspace besitzt den Plan."
    }
  }],
  "reason": "Kein Mehrbenutzerbetrieb oder Server erforderlich.",
  "confidence": 0.88,
  "reversible": true,
  "dependsOn": ["usage-mode"],
  "status": "recommended"
}
```

`confidence` unterstützt die Darstellung, entscheidet aber nicht allein über
Autonomie. Risiko und Reversibilität haben Vorrang.

## Benutzeroberfläche

Die native Inline-Visualisierung in einer Codex-Antwort soll zeigen:

- aktiven Entscheidungspfad
- alternative Optionen an jedem Knoten
- drei bis vier Optionen je Entscheidung, jeweils mit ausklappbarer
  Kurzbeschreibung
- Klick auf einen Optionstitel wählt die Option; nur der separate Pfeil klappt
  ihre Beschreibung auf
- Aktionen zum gemeinsamen Auf- und Einklappen aller Details
- Kennzeichnung von KI-Empfehlung und menschlicher Auswahl
- kurze Begründung und Sicherheitsgrad
- ausklappbare Details je Entscheidung mit Begründung, Abhängigkeiten und
  Reversibilität
- nächsten blockierenden menschlichen Entscheidungspunkt
- Auswirkungen einer geplanten Änderung
- Aktion zum Wechseln einer früheren Entscheidung
- Aktion zum Bestätigen und Fortsetzen

Beim Wechsel darf der bisherige Pfad nicht still überschrieben werden. Die UI
zeigt vor der Neuberechnung, welcher abhängige Teilbaum ungültig wird.

## MVP

Der erste nutzbare Stand umfasst:

- einen neuen Skill als Orchestrator, ohne bestehende Grill-with-Docs-Skills zu
  forken
- eine interaktive, frameworkfreie HTML-Visualisierung direkt in Codex
- eine JSON-Datei als persistierten Workflow-Zustand
- Klassifikation in `auto`, `review`, `human` und `derived`
- Baumansicht, Wechsel früherer Entscheidungen und gezielte Neuberechnung
- Export des aktuellen Pfads als Markdown oder JSON

Der Skill enthält Workflow- und Stop-Regeln. Ein Stdlib-Skript übernimmt
deterministische Zustandsänderungen, Markdown-Export und Rendering. Die
eigentliche KI-Arbeit bleibt beim ausführenden Agenten.

## Nicht Teil des MVP

- Benutzerkonten oder Mehrbenutzerbetrieb
- Cloud-Hosting oder Datenbankdienst
- eigener lokaler Webserver
- Echtzeit-Kollaboration
- eigene Modell- oder Providerintegration
- generischer visueller Workflow-Editor
- automatische Änderung bestehender Grill-with-Docs-Skills
- vollständige Historie mit Merge verschiedener Entscheidungszweige

## Sicherheits- und Qualitätsregeln

- Projektcode und Dokumentation vor Empfehlungen untersuchen.
- Keine Empfehlung allein aus allgemeiner Popularität ableiten.
- Unsicherheit sichtbar machen; fehlende Fakten nicht erfinden.
- Sicherheitskritische oder irreversible Schritte nicht automatisch bestätigen.
- Abhängige Entscheidungen nach einem Wechsel nicht ungeprüft weiterverwenden.
- Bestehende Validierung, Authentifizierung und Schutzmaßnahmen nicht umgehen.

## Akzeptanzkriterien für den MVP

- Ein Beispielworkflow läuft automatisch über mindestens zwei `auto`- oder
  `review`-Knoten bis zu einem `human`-Knoten.
- Die UI zeigt gewählten Pfad, Alternativen und Begründungen.
- Eine frühere Wahl kann geändert werden.
- Nur abhängige Nachfolger werden danach ungültig und neu berechnet.
- Zustand bleibt nach Browser-Neuladen erhalten.
- Aktueller Pfad lässt sich als Markdown oder JSON exportieren.
- Kein Netzwerkzugriff ist für den lokalen Prototyp erforderlich.
- Kompakter und visueller Modus nutzen dieselben Entscheidungs- und
  Human-Gate-Regeln.
- Ein Wechsel von kompakt zu visuell übernimmt bereits bekannte Entscheidungen.

## Festgehaltene Entscheidungen

- Umsetzung als Skill plus native Codex-Inline-Visualisierung.
- Bestehende Grill-with-Docs-Skills zunächst umschließen, nicht verändern.
- Lokaler, einfacher MVP vor Plattform oder Produktisierung.
- Mensch bleibt letzte Instanz für wesentliche Entscheidungen.
- Workspace-JSON ist Source of Truth; die Visualisierung ist nur eine Ansicht.

## Offene Entscheidungen

Vor Implementierung noch anhand der vorhandenen Grill-with-Docs-Skills prüfen:

- Welche konkreten Skills und Ausgabeformate werden integriert?
- Welche konkreten zusätzlichen Grill-with-Docs-Varianten werden integriert?
- Soll ein Wechsel einen alten Zweig nur verwerfen oder als lesbare Historie
  behalten?
- Wo wird der Skill später installiert: im Projekt oder im persönlichen
  Codex-Skill-Verzeichnis?

## Nächster Schritt

Skill mit einem realen Planungsproblem vorwärts testen. Dabei besonders prüfen,
ob Human-Gates weder zu häufig noch zu spät gesetzt werden.
