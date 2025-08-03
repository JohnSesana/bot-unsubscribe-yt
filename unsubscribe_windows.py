"""
Unsubscribe from every channel on https://www.youtube.com/feed/channels
Windows edition (tested on Windows 10 / 11 + Chrome 119 + Selenium 4.20).

Prereqs
-------
1. Google Chrome installed (or Chromium-based Edge – see note below).
2. Matching chromedriver.exe on your PATH, or let Selenium Manager
   download it automatically (Selenium ≥ 4.6 does this).
3. `pip install selenium`.

Usage
-----
> py yt_mass_unsub_win.py
"""


import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ── ADJUST THESE TWO LINES TO POINT AT YOUR CHROME PROFILE ────────────────
# Windows keeps Chrome profiles in:
#   %LOCALAPPDATA%\Google\Chrome\User Data\<ProfileName>
# For most users ProfileName is "Default".
PROFILE_DIR  = Path(os.environ["LOCALAPPDATA"]) / "Chromium" / "User Data"
PROFILE_NAME = "Default"
#   If you’re using Microsoft Edge instead of Chrome:
#   PROFILE_DIR  = Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "Edge" / "User Data"
# ──────────────────────────────────────────────────────────────────────────


# --- XPaths (unchanged) ----------------------------------------------------
SUB_BTN = ('//ytd-subscribe-button-renderer[@subscribed]'
           '//button[contains(@aria-label,"Subscribed") '
           '      or contains(translate(normalize-space(.),'
           '"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),'
           '"subscribed")]')

MENU_UNSUB = ('//tp-yt-paper-item['
              'contains(translate(normalize-space(.),'
              '"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),'
              '"unsubscribe")]')

SHEET_UNSUB = ('//yt-confirm-dialog-renderer'
               '//button[@aria-label="Unsubscribe" '
               ' or span[contains(translate(.,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),'
               '"unsubscribe")]]')
# ---------------------------------------------------------------------------


def chrome() -> webdriver.Chrome:
    """Launch Chrome with the chosen profile in full-screen mode."""
    o = Options()
    o.add_argument(f"--user-data-dir={PROFILE_DIR}")
    o.add_argument(f"--profile-directory={PROFILE_NAME}")
    o.add_argument("--no-first-run")
    o.add_argument("--password-store=basic")
    o.add_argument("--start-maximized")

    # On Windows you usually don’t need to set a binary location. If you’re
    # running a portable build, uncomment the next line and point at chrome.exe
    # o.binary_location = r"C:\Path\To\chrome.exe"

    return webdriver.Chrome(options=o)


def scroll_all(driver: webdriver.Chrome) -> None:
    """Scroll to the bottom of the page (two passes with no growth = done)."""
    unchanged = 0
    last = driver.execute_script("return document.body.scrollHeight")
    while unchanged < 2:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.7)
        h = driver.execute_script("return document.body.scrollHeight")
        unchanged = unchanged + 1 if h == last else 0
        last = h


def safe_click(driver: webdriver.Chrome, el) -> None:
    """Attempt a real click; fallback to JS if it fails (e.g. covered)."""
    try:
        ActionChains(driver).move_to_element(el).click().perform()
    except Exception:
        driver.execute_script("arguments[0].click()", el)


def main() -> None:
    driver = chrome()
    wait = WebDriverWait(driver, 5)

    driver.get("https://www.youtube.com/feed/channels")

    # If a “Manage” link is present, click it once
    try:
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//yt-formatted-string[.="Manage"]')
            )
        ).click()
        time.sleep(0.5)
    except Exception:
        pass

    scroll_all(driver)

    count = 0
    while True:
        btns = driver.find_elements(By.XPATH, SUB_BTN)
        if not btns:
            break

        btn = btns[0]
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", btn)
        safe_click(driver, btn)  # open bell menu

        try:
            menu_item = wait.until(
                EC.element_to_be_clickable((By.XPATH, MENU_UNSUB))
            )
            safe_click(driver, menu_item)  # click “Unsubscribe” in menu
        except Exception:
            print("⚠️  bell menu not found; skipping")
            continue

        try:
            confirm = wait.until(
                EC.element_to_be_clickable((By.XPATH, SHEET_UNSUB))
            )
            safe_click(driver, confirm)  # confirm dialog
            count += 1
            print(f"❌  {count} unsubscribed")
        except Exception:
            print("⚠️  confirmation sheet not found; skipping")

        time.sleep(0.35)  # fast but stable

    print(f"🎉  Finished – {count} channels removed. Close the window manually.")
    # driver.quit()  # leave browser open if you like


if __name__ == "__main__":
    main()
