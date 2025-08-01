from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager
import requests
import random
import time
import os

# --- ДАННЫЕ ДЛЯ ВХОДА ---
LOGIN = os.environ["LOGIN"]
PASSWORD = os.environ["PASSWORD"]

# --- TELEGRAM ---
TELEGRAM_BOT_TOKEN = os.environ["TG_TOKEN"]
CHAT_ID = os.environ["TG_CHAT_ID"]

# --- НАСТРОЙКИ FIREFOX ---
profile = FirefoxProfile()
profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0")
options = Options()
options.headless = True

# --- TELEGRAM СООБЩЕНИЕ ---
def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {'chat_id': CHAT_ID, 'text': text}
        requests.post(url, data=data)
    except Exception as e:
        print("Ошибка Telegram:", e)

# --- ОСНОВНОЙ СКРИПТ ---
def run_bonus_script():
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get("https://loliland.ru/ru/login")
        time.sleep(random.uniform(2.5, 4.5))

        if "cabinet/logout" in driver.page_source:
            print("🔁 Уже залогинен. Переход к бонусу.")
            send_telegram_message("🔁 Уже авторизован. Переход к бонусу.")
        else:
            login_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "login"))
            )
            password_input = driver.find_element(By.NAME, "password")

            actions = ActionChains(driver)
            actions.move_to_element(login_input).click().perform()
            time.sleep(random.uniform(1, 2))
            login_input.send_keys(LOGIN)

            actions.move_to_element(password_input).click().perform()
            time.sleep(random.uniform(1, 2))
            driver.execute_script("arguments[0].removeAttribute('readonly')", password_input)
            password_input.send_keys(PASSWORD)
            time.sleep(random.uniform(0.5, 1.5))
            password_input.submit()
            time.sleep(2)

        driver.get("https://loliland.ru/ru/cabinet/bonus")
        time.sleep(3)

        current_url = driver.current_url
        if "/login" in current_url:
            send_telegram_message("❌ Не удалось войти в аккаунт LoliLand.")
            return

        page = driver.page_source

        if "Бонус получен" in page or "забрали" in page:
            send_telegram_message("✅ Бонус успешно получен!")
        elif "уже получили" in page:
            send_telegram_message("ℹ️ Бонус уже был получен ранее.")
        else:
            send_telegram_message("⚠️ Не удалось определить статус бонуса.")

    except Exception as e:
        send_telegram_message(f"❗ Ошибка скрипта: {e}")
    finally:
        driver.quit()

# --- ЗАПУСК ---
if __name__ == "__main__":
    run_bonus_script()
