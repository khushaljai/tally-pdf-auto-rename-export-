# Tally Auto Rename

Automatic PDF renaming utility for Tally Prime exports.

Created by Khushal Jain.

---

# Overview

Tally Auto Rename is a lightweight Windows tray utility that automatically watches a folder for newly exported Tally PDF files and renames them intelligently using extracted invoice or ledger data.

The application was specifically designed for Tally Prime PDF exports and works without:
- TDL modifications
- OCR
- internet connection
- cloud services
- database setup

The utility is optimized for low-resource systems and can run continuously in the background with minimal CPU and RAM usage.

---

# Supported Export Types

Currently supported:

## Sales Invoices

Automatically renames sales invoices using:
- Invoice Number
- Party Name

Example:

```text
272 - khushal SALES.pdf
```

---

## Purchase Invoices

Automatically renames purchase invoices using:
- Supplier Invoice Number
- Supplier Name

Example:

```text
KH-189 - khushal PURCHASE.pdf
```

---

## Ledger Exports

Automatically renames ledger exports using:
- Ledger Name
- Date Range

Example:

```text
KHUSHAL JAIN Apr2026 to May2026 LEDGER.pdf
```

---

# Features

- Automatic folder monitoring
- Real-time PDF detection
- Tally-specific PDF parsing
- Duplicate event protection
- Handles repeated Tally filenames
- Collision-safe renaming
- System tray integration
- Session-only logging
- Startup shortcut support
- Configurable watch folder
- No Python installation required
- Works fully offline

---

# System Requirements

## Minimum Requirements

- Windows 7 / 10 / 11
- Dual-core processor
- 2 GB RAM
- 150 MB free disk space

## Recommended Requirements

- Windows 10 / 11
- Intel i3 or equivalent
- 4 GB RAM
- SSD recommended

---

# Important Notes

This application supports only:
- text-based Tally PDF exports

This application does NOT support:
- scanned PDFs
- image PDFs
- OCR-based extraction
- handwritten invoices

---

# Installation

1. Download:

```text
TallyAutoRenameSetup.exe
```

2. Run installer as Administrator.

3. Select your Tally export folder during setup.

4. Finish installation.

5. The application will automatically start in the system tray.

---

# Configuration

The application stores settings inside:

```text
config.json
```

Example:

```json
{
    "watch_folder": "C:\\tallydownloads"
}
```

You can modify the watched folder later by editing the config file and restarting the application.

---

# Tray Menu Options

The tray icon supports:

- Start Monitoring
- Stop Monitoring
- Show Logs
- Open Watch Folder
- Exit

---

# Logging

Logs are session-only.

The application:
- creates a fresh log each launch
- deletes logs on exit

No persistent log history is stored.

---

# How It Works

The application uses:
- watchdog for real-time folder monitoring
- PyMuPDF for PDF text extraction
- Tally-specific parsing logic for intelligent renaming

The app is event-driven and does not continuously scan the disk, resulting in very low idle CPU usage.

---

# Example Workflow

Tally export:

```text
Sales XXX_272_26-27.pdf
```

Automatically renamed to:

```text
272 - KHUSHAL SALES.pdf
```

---

# Known Limitations

- Designed specifically for Tally Prime exports
- PDF structure changes may break detection
- OCR/scanned invoices are unsupported
- Extremely unusual invoice formats may fail parsing

---

# Privacy

This application:
- does not upload data
- does not use internet access
- does not collect telemetry
- does not send files externally

All processing occurs locally on the user's computer.

---

# License

MIT License

Copyright (c) 2026 Khushal Jain

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to:
- use
- copy
- modify
- merge
- publish
- distribute
- sublicense
- sell copies of the Software

subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

---

# Author

Khushal Jain

India

---

# Version

Current Version:
```text
v1.0.0
```
