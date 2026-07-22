# Interactive Grill

Dieser Kontext beschreibt einen Grill-with-Docs-Workflow, der selbstständig bis
zur nächsten wesentlichen menschlichen Entscheidung arbeitet.

## Language

**Entscheidungsknoten**:
Eine Frage mit Optionen, Abhängigkeiten, Empfehlung und aktuellem Status.
_Avoid_: Schritt, Prompt

**Human-Gate**:
Ein Entscheidungsknoten, an dem der autonome Lauf vor einer wesentlichen
menschlichen Wahl anhält.
_Avoid_: Approval, Rückfrage

**Aktiver Pfad**:
Die aktuell gewählte Folge gültiger Entscheidungsknoten.
_Avoid_: Happy Path

**Abhängiger Teilbaum**:
Alle direkten und transitiven Entscheidungen, deren Gültigkeit von einem
früheren Entscheidungsknoten abhängt.
_Avoid_: Rest des Workflows

**Source of Truth**:
Die persistierte JSON-Datei, aus der Entscheidungsbaum und Export erzeugt werden.
Die Inline-Visualisierung ist keine dauerhafte Zustandsquelle.
_Avoid_: UI-Zustand
