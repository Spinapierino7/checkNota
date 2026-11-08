# Check Nota Automation

This repository contains a small Python script that periodically checks a value on a website and notifies you by email when the value changes.

## Files
- `check_note.py` – Main script that performs the request, parses the page, compares the value with the last stored value, and sends an email if it changed.
- `requirements.txt` – Python dependencies.
- `.gitignore` – Files/folders ignored by git.
- `README.md` – This documentation.

## Setup
1. **Create a virtual environment** (recommended) and install dependencies:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1   # or Activate.bat for cmd
   pip install -r requirements.txt
   ```
2. **Create a `.env` file** (or set environment variables in the system) with the configuration. Example:
   ```
   NOTE_PAGE_URL=https://example.com/nota
   NOTE_POST_URL=https://example.com/nota   # same as PAGE_URL if the form uses GET
   NOTE_FIELD_NAME=numero
   NOTE_NUMBER=12345
   NOTE_STATE_FILE=state.json

   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your.email@gmail.com
   SMTP_PASSWORD=your_app_password
   NOTIFY_EMAIL=your.email@gmail.com
   ```
   The script reads these variables via `os.getenv`. You can also export them directly in the shell before running the script.

3. **Initialize git and push**:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit – check_note automation"
   # Add your remote repository (GitHub, GitLab, etc.)
   git remote add origin https://github.com/youruser/yourrepo.git
   git push -u origin master
   ```

## Scheduling the script
Windows does not have `cron` natively, but you can use **Task Scheduler** (or the `schtasks` CLI) to run the script on a schedule without keeping your PC on.

### Using `schtasks`
```powershell
# Run every hour (adjust /SC and /MO as needed)
SCHTASKS /Create /SC HOURLY /MO 1 /TN "CheckNota" /TR "C:\\Users\\pieri\\Desktop\\Script Nota AM2\\venv\\Scripts\\python.exe C:\\Users\\pieri\\Desktop\\Script Nota AM2\\check_note.py" /RL HIGHEST /F
```
- `/SC` – schedule frequency (MINUTE, HOURLY, DAILY, WEEKLY, ...).
- `/MO` – modifier (e.g., every 30 minutes: `/SC MINUTE /MO 30`).
- `/TR` – the command to run. Adjust the full path if you installed Python elsewhere.

You can also create the task via the GUI:
1. Open **Task Scheduler** → *Create Basic Task*.
2. Name it (e.g., *Check Nota*).
3. Choose *Daily* or *Weekly* and set the start time.
4. In *Action* select *Start a program* and browse to `python.exe` inside your virtual‑env, then add the script path as an argument.
5. Finish and make sure the task is set to *Run whether user is logged on or not* and *Run with highest privileges*.

### Using a simple batch file (optional)
If you prefer a `.bat` wrapper:
```bat
@echo off
C:\Users\pieri\Desktop\Script Nota AM2\venv\Scripts\python.exe C:\Users\pieri\Desktop\Script Nota AM2\check_note.py
```
Save it as `run_check.bat` and point the scheduled task to that file.

## Email notifications
The script uses `smtplib`. For Gmail you need an **App Password** (or enable *Less secure app access* if still allowed). Other providers work similarly – just change `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, and `SMTP_PASSWORD`.

## Customising the parser
The current implementation looks for an element with `id="resultado"`. Adjust the `fetch_current_value` function in `check_note.py` to match the actual HTML structure of the page you are querying (different selectors, JSON APIs, etc.).

## Troubleshooting
- **Missing environment variables** – The script will print a warning and skip the email step.
- **Network errors** – Verify the URL and that the site does not require authentication or captcha (the script cannot bypass captchas).
- **Task not running** – Check Task Scheduler's history or run the command manually to see any errors.

---
Happy monitoring!
