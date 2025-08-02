#!/usr/bin/env python3
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ── SET THESE TWO LINES TO YOUR CHROME / CHROMIUM PROFILE ────────────────
PROFILE_DIR  = Path("/home/{YOUR USER}/.config/chromium")   # --user-data-dir
PROFILE_NAME = "Default"                                # --profile-directory
# ──────────────────────────────────────────────────────────────────────────

# --- XPaths -----------------------------------------------------------------
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

def chrome():
    o = Options()
    o.add_argument(f"--user-data-dir={PROFILE_DIR}")
    o.add_argument(f"--profile-directory={PROFILE_NAME}")
    o.add_argument("--no-first-run --password-store=basic --start-maximized")
    return webdriver.Chrome(options=o)

def scroll_all(driver):
    unchanged = 0
    last = driver.execute_script("return document.body.scrollHeight")
    while unchanged < 2:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.7)
        h = driver.execute_script("return document.body.scrollHeight")
        unchanged = unchanged + 1 if h == last else 0
        last = h

def safe_click(driver, el):
    try:
        ActionChains(driver).move_to_element(el).click().perform()
    except Exception:
        driver.execute_script("arguments[0].click()", el)

driver = chrome()
wait   = WebDriverWait(driver, 10)

driver.get("https://www.youtube.com/feed/channels")

# If a “Manage” link exists click it once
try:
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//yt-formatted-string[.="Manage"]'))).click()
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
    safe_click(driver, btn)                          # open bell menu

    try:
        menu_item = wait.until(EC.element_to_be_clickable((By.XPATH, MENU_UNSUB)))
        safe_click(driver, menu_item)                # click Unsubscribe in menu
    except Exception:
        print("⚠️  bell menu not found; skipping")
        continue

    try:
        confirm = wait.until(EC.element_to_be_clickable((By.XPATH, SHEET_UNSUB)))
        safe_click(driver, confirm)                  # confirm sheet
        count += 1
        print(f"❌  {count} unsubscribed")
    except Exception:
        print("⚠️  confirmation sheet not found; skipping")

    time.sleep(0.35)                                 # fast but stable

print(f"🎉  Finished – {count} channels removed. Close the window manually.")
# (No driver.quit(); leave browser open)