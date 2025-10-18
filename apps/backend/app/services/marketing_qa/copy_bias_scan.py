# toy rules to catch India-EN issues; expand later
RULES = [
    ("call me back with money", "May signal high intent in Indian English; avoid negative scoring."),
    ("expert", "Consider 'specialist' or 'advisor' for trust tone."),
]

def scan_copy(text: str) -> dict:
    hits = [hint for phrase, hint in RULES if phrase.lower() in text.lower()]
    return {
        "check":"copy_bias_scan",
        "status": "warning" if hits else "pass",
        "details":{"findings": hits}
    }
