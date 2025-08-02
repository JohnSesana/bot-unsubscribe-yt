# YouTube-Mass-Unsubscribe Bot

Automate the boring job of unsubscribing from **every channel** on your
[YouTube “All subscriptions” page](https://www.youtube.com/feed/channels).

The script opens Chrome / Chromium with your real profile, scrolls until
all channel tiles are loaded, then for **each** channel it

1. clicks **Subscribed ▾** (bell menu)  
2. selects **Unsubscribe** in the menu  
3. clicks **Unsubscribe** in the confirmation sheet  

You watch the count tick up in your terminal; the browser stays open so
you can close it when you’re happy.

---

## Features

* **Works with any logged-in Chrome/Chromium profile** (no Google login
  automation → no “insecure browser” errors)
* Handles the current *(Aug 2025)* two-step **bell menu + confirmation
  sheet** flow
* Fast — ~0.4 s per channel
* Leaves the browser window open for manual review
* Zero Selenium boilerplate in your repo — just a single script

---

## Prerequisites

| What                       | Arch / Manjaro command                              |
|----------------------------|-----------------------------------------------------|
| **Chromium** (or Chrome)   | `sudo pacman -S chromium`                           |
| **Python ≥ 3.9**           | already on most distros                             |
| **pip / venv**             | `sudo pacman -S python-pip python-virtualenv`       |
| **Selenium 4**             | installed via `pip`                                 |

---

## Quick start

```bash
# 1 clone & enter repo
git clone https://github.com/JohnSesana/bot-unsubscribe-yt.git
cd bot-unsubscribe-yt

# 2 create isolated env
python -m venv venv
source venv/bin/activate
pip install --upgrade pip

# 3 install deps
pip install selenium undetected-chromedriver beautifulsoup4

# 4 Run
python unsubscribe.py
