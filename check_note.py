import os
import sys
import smtplib
import json
from email.message import EmailMessage
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import sys
import smtplib
import json
from email.message import EmailMessage
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# Configuration ---------------------------------------------------------------
# The URL of the page that contains the note form
PAGE_URL = os.getenv("NOTE_PAGE_URL", "https://example.com/nota")
# The POST endpoint (if the form uses POST) – if the form is GET just use PAGE_URL
POST_URL = os.getenv("NOTE_POST_URL", PAGE_URL)
# The name of the input field that receives the number (as seen in the HTML form)
FIELD_NAME = os.getenv("NOTE_FIELD_NAME", "numero")
# The number you want to query – you can change it via env var or keep constant
NUMBER_TO_QUERY = os.getenv("NOTE_NUMBER", "12345")
# Path to a JSON file where we store the last known value
STATE_FILE = os.getenv("NOTE_STATE_FILE", "state.json")
# Email settings --------------------------------------------------------------
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")  # full email address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT = os.getenv("NOTIFY_EMAIL")


def load_last_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("value")


def save_state(value):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"value": value, "timestamp": datetime.utcnow().isoformat()}, f)


def fetch_current_value():
    # The form may be simple GET with a query string, adjust if POST is required.
    params = {FIELD_NAME: NUMBER_TO_QUERY}
    try:
        response = requests.get(POST_URL, params=params, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error contacting site: {e}", file=sys.stderr)
        return None

    # Parse the HTML – this part will likely need tweaking for the actual site.
    soup = BeautifulSoup(response.text, "html.parser")
    # Example: the value we care about is inside an element with id="resultado"
    result_elem = soup.select_one("#resultado")
    if not result_elem:
        print("Could not find result element on the page", file=sys.stderr)
        return None
    return result_elem.get_text(strip=True)


def send_email(subject: str, body: str):
    if not all([SMTP_USER, SMTP_PASSWORD, RECIPIENT]):
        print("Missing email configuration – skipping notification")
        return
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print("Notification email sent")
    except Exception as e:
        print(f"Failed to send email: {e}", file=sys.stderr)


def main():
    current = fetch_current_value()
    if current is None:
        sys.exit(1)
    last = load_last_state()
    if last is None:
        # First run – just store the value.
        save_state(current)
        print(f"Stored initial value: {current}")
        return
    if current != last:
        # Value changed – notify and update state.
        subject = f"[Nota] Valor cambiado para {NUMBER_TO_QUERY}"
        body = (
            f"El valor consultado en {PAGE_URL} ha cambiado.\n\n"
            f"Anterior: {last}\nActual: {current}\n"
            f"Hora (UTC): {datetime.utcnow().isoformat()}"
        )
        send_email(subject, body)
        save_state(current)
        print("Change detected and notified")
    else:
        print("No change detected")

if __name__ == "__main__":
    main()
