import os
import re
import sys
import time
import fitz
import subprocess

from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import pystray
from PIL import Image, ImageDraw

# ======================================================
# BASE DIRECTORY
# ======================================================

if getattr(sys, 'frozen', False):

    BASE_DIR = os.path.dirname(
        sys.executable
    )

else:

    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

# ======================================================
# CONFIG
# ======================================================

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "config.json"
)

DEFAULT_WATCH_FOLDER = r"C:\tallydownloads"

# ------------------------------------------------------
# Create config if missing
# ------------------------------------------------------

if not os.path.exists(CONFIG_FILE):

    try:

        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                '{\n'
                '    "watch_folder": '
                '"C:\\\\tallydownloads"\n'
                '}'
            )

    except Exception as e:

        print(
            f"Failed to create config: {e}"
        )

# ------------------------------------------------------
# Read config
# ------------------------------------------------------

WATCH_FOLDER = DEFAULT_WATCH_FOLDER

try:

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        config_text = f.read()

    match = re.search(
        r'"watch_folder"\s*:\s*"([^"]+)"',
        config_text
    )

    if match:

        WATCH_FOLDER = (
            match
            .group(1)
            .replace("\\\\", "\\")
        )

except Exception as e:

    print(
        f"Failed to read config: {e}"
    )

# ======================================================
# SESSION LOG
# ======================================================

LOG_FILE = os.path.join(
    BASE_DIR,
    "session.log"
)

# Delete old session log on startup
if os.path.exists(LOG_FILE):

    try:
        os.remove(LOG_FILE)

    except:
        pass

# ======================================================
# GLOBALS
# ======================================================

processed_files = set()

observer = None
monitoring = False

# ======================================================
# LOGGING
# ======================================================

def log(message):

    timestamp = time.strftime("%H:%M:%S")

    line = f"[{timestamp}] {message}"

    print(line)

    try:

        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(line + "\n")

    except:
        pass

# ======================================================
# HELPERS
# ======================================================

def clean_filename(name):

    return re.sub(
        r'[\\/*?:"<>|]',
        "",
        name
    ).strip()


def clean_invoice_number(invoice_no):

    invoice_no = re.sub(
        r"[\\/]",
        "_",
        invoice_no
    )

    return invoice_no.strip()


def extract_text(pdf_path):

    text = ""

    try:

        doc = fitz.open(pdf_path)

        for page in doc:

            text += page.get_text()

        doc.close()

    except Exception as e:

        log(f"PDF read error: {e}")

    return text


def wait_for_file_complete(file_path, timeout=30):

    previous_size = -1

    start = time.time()

    while time.time() - start < timeout:

        try:

            current_size = os.path.getsize(file_path)

            if current_size == previous_size:
                return True

            previous_size = current_size

        except:
            pass

        time.sleep(1)

    return False

# ======================================================
# EXTRACT DETAILS
# ======================================================

def extract_invoice_details(text):

    invoice_no = None
    party_name = None
    doc_type = "UNKNOWN"

    # ==================================================
    # SALES
    # ==================================================

    sales_match = re.search(
        r"Buyer\s*\(Bill to\)\s*([A-Z0-9 &.,()-]+)",
        text,
        re.IGNORECASE
    )

    if sales_match:

        doc_type = "SALES"

        party_name = sales_match.group(1).strip()

        invoice_match = re.search(
            r"Invoice No\.\s*([\w/-]+)",
            text,
            re.IGNORECASE
        )

        if invoice_match:

            invoice_no = invoice_match.group(1).strip()

            invoice_no = re.sub(
                r"/\d{2}-\d{2}$",
                "",
                invoice_no
            )

            invoice_no = clean_invoice_number(
                invoice_no
            )

        return invoice_no, party_name, doc_type

    # ==================================================
    # PURCHASE
    # ==================================================

    purchase_match = re.search(
        r"Supplier\s*\(Bill from\)\s*([A-Z0-9 &.,()-]+)",
        text,
        re.IGNORECASE
    )

    if purchase_match:

        doc_type = "PURCHASE"

        party_name = purchase_match.group(1).strip()

        supplier_invoice_match = re.search(
            r"Supplier Invoice No\.\s*&\s*Date\.\s*([^\s]+)",
            text,
            re.IGNORECASE
        )

        if supplier_invoice_match:

            invoice_no = (
                supplier_invoice_match
                .group(1)
                .strip()
            )

            invoice_no = clean_invoice_number(
                invoice_no
            )

        return invoice_no, party_name, doc_type

    # ==================================================
    # LEDGER
    # ==================================================

    if "Ledger Account" in text:

        doc_type = "LEDGER"

        ledger_match = re.search(
            r"E-Mail.*?\n([A-Z0-9 &.,()-]+)\nLedger Account",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if ledger_match:

            party_name = (
                ledger_match
                .group(1)
                .strip()
            )

        date_match = re.search(
            r"(\d{1,2}-[A-Za-z]{3}-\d{2})\s+to\s+(\d{1,2}-[A-Za-z]{3}-\d{2})",
            text
        )

        if date_match:

            start_date = date_match.group(1)
            end_date = date_match.group(2)

            def format_date(date_str):

                try:

                    dt = time.strptime(
                        date_str,
                        "%d-%b-%y"
                    )

                    return time.strftime(
                        "%b%Y",
                        dt
                    )

                except:

                    return date_str

            start_formatted = format_date(
                start_date
            )

            end_formatted = format_date(
                end_date
            )

            invoice_no = (
                f"{start_formatted} to "
                f"{end_formatted}"
            )

        return invoice_no, party_name, doc_type

    return None, None, "UNKNOWN"

# ======================================================
# RENAME LOGIC
# ======================================================

def rename_pdf(pdf_path):

    pdf_path = Path(pdf_path)

    # Ignore stale events
    if not pdf_path.exists():
        return

    # Unique file identity
    file_id = (
        str(pdf_path),
        os.path.getmtime(pdf_path)
    )

    # Skip duplicate watchdog events
    if file_id in processed_files:
        return

    processed_files.add(file_id)

    # Skip already renamed files
    if re.search(
        r"\s(SALES|PURCHASE|LEDGER)(\s\(\d+\))?$",
        pdf_path.stem,
        re.IGNORECASE
    ):
        return

    log(f"Detected: {pdf_path.name}")

    # Wait until file finishes writing
    if not wait_for_file_complete(pdf_path):

        log("File still busy")
        return

    text = extract_text(pdf_path)

    invoice_no, party_name, doc_type = (
        extract_invoice_details(text)
    )

    if not invoice_no:

        log("Invoice/date not found")
        return

    if not party_name:

        log("Party/Ledger name not found")
        return

    # ==================================================
    # FINAL FILENAME
    # ==================================================

    if doc_type == "LEDGER":

        new_name = (
            f"{party_name} "
            f"{invoice_no} "
            f"LEDGER.pdf"
        )

    else:

        new_name = (
            f"{invoice_no} - "
            f"{party_name} "
            f"{doc_type}.pdf"
        )

    new_name = clean_filename(new_name)

    new_path = pdf_path.with_name(new_name)

    # Prevent overwrite
    counter = 1

    while new_path.exists():

        if doc_type == "LEDGER":

            new_name = (
                f"{party_name} "
                f"{invoice_no} "
                f"LEDGER "
                f"({counter}).pdf"
            )

        else:

            new_name = (
                f"{invoice_no} - "
                f"{party_name} "
                f"{doc_type} "
                f"({counter}).pdf"
            )

        new_name = clean_filename(new_name)

        new_path = pdf_path.with_name(new_name)

        counter += 1

    try:

        os.rename(pdf_path, new_path)

        log(
            f"{doc_type} renamed -> "
            f"{new_path.name}"
        )

    except Exception as e:

        log(f"Rename failed: {e}")

# ======================================================
# WATCHDOG
# ======================================================

class PDFHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        if event.src_path.lower().endswith(".pdf"):

            time.sleep(2)

            if not os.path.exists(event.src_path):
                return

            rename_pdf(event.src_path)

# ======================================================
# MONITOR CONTROL
# ======================================================

def start_monitoring(icon=None, item=None):

    global observer
    global monitoring

    if monitoring:

        log("Monitoring already running")
        return

    event_handler = PDFHandler()

    observer = Observer()

    observer.schedule(
        event_handler,
        WATCH_FOLDER,
        recursive=False
    )

    observer.start()

    monitoring = True

    log("Monitoring started")


def stop_monitoring(icon=None, item=None):

    global observer
    global monitoring

    if not monitoring:

        log("Monitoring already stopped")
        return

    observer.stop()
    observer.join()

    monitoring = False

    log("Monitoring stopped")

# ======================================================
# MENU ACTIONS
# ======================================================

def show_logs(icon=None, item=None):

    subprocess.Popen(
        ["notepad.exe", LOG_FILE]
    )


def open_folder(icon=None, item=None):

    os.startfile(WATCH_FOLDER)


def on_exit(icon, item):

    stop_monitoring()

    # Delete session log on exit
    try:

        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

    except:
        pass

    icon.stop()

# ======================================================
# TRAY ICON
# ======================================================

def create_icon():

    image = Image.new(
        "RGB",
        (64, 64),
        "white"
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (16, 16, 48, 48),
        fill="black"
    )

    return image

# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    if not os.path.exists(WATCH_FOLDER):

        print(
            f"Folder not found:\n"
            f"{WATCH_FOLDER}"
        )

        exit()

    log("Application started")

    start_monitoring()

    icon = pystray.Icon(
        "TallyRename",
        create_icon(),
        "Tally Auto Rename",

        menu=pystray.Menu(

            pystray.MenuItem(
                "Start Monitoring",
                start_monitoring
            ),

            pystray.MenuItem(
                "Stop Monitoring",
                stop_monitoring
            ),

            pystray.MenuItem(
                "Show Logs",
                show_logs
            ),

            pystray.MenuItem(
                "Open Folder",
                open_folder
            ),

            pystray.MenuItem(
                "Exit",
                on_exit
            )
        )
    )

    icon.run()