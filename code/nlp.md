import re
import spacy
from typing import Tuple, List, Optional

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

# List of supported currencies (ISO 4217 codes)
CURRENCY_CODES = {"USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF", "CNY", "NZD", "SGD", "HKD"}

# Map of time units to API-friendly suffixes
TIME_UNIT_MAP = {
    "day": "D",
    "days": "D",
    "week": "W",
    "weeks": "W",
    "month": "M",
    "months": "M",
    "year": "Y",
    "years": "Y"
}

def extract_currencies(text: str) -> List[str]:
    words = set(re.findall(r"\b[A-Z]{3}\b", text.upper()))
    return list(words & CURRENCY_CODES)

def extract_time_period(text: str) -> Optional[str]:
    match = re.search(r"(last|past)?\s*(\d+)\s*(day|days|week|weeks|month|months|year|years)", text, re.IGNORECASE)
    if match:
        number = match.group(2)
        unit = match.group(3).lower()
        return f"{number}{TIME_UNIT_MAP[unit]}"
    return None

def extract_intent(text: str) -> Optional[str]:
    lowered = text.lower()
    if "historical rate" in lowered or "history of" in lowered or "past rate" in lowered:
        return "historical_rates"
    elif "current rate" in lowered or "live rate" in lowered or "today" in lowered:
        return "current_rates"
    return None

def parse_query(text: str) -> dict:
    doc = nlp(text)
    intent = extract_intent(text)
    currencies = extract_currencies(text)
    time_period = extract_time_period(text)

    # Return first two currencies in order of appearance
    ordered_currencies = []
    for token in doc:
        if token.text.upper() in currencies and token.text.upper() not in ordered_currencies:
            ordered_currencies.append(token.text.upper())

    currency_pair = None
    if len(ordered_currencies) >= 2:
        currency_pair = f"{ordered_currencies[0]}/{ordered_currencies[1]}"

    return {
        "intent": intent,
        "currency_pair": currency_pair,
        "time_period": time_period
    }

# Example usage
query = "What are the historical rates for USD and EUR for the last 2 months?"
result = parse_query(query)
print(result)
