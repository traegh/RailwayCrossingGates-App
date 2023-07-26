import threading
import random
import time
import os
from colorama import init, Fore, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import re
import html
import pymysql

init()
# Basic anti-bot detection measures pt1
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G973F Build/RP1A.201005.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.71 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.50",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.6; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 OPR/80.0.4170.72"
]

last_timetable = None

# Basic anti-bot detection measures pt2
def configure_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    user_agent = random.choice(user_agents)
    options.add_argument(f"--user-agent={user_agent}")
    resolutions = [
        (1920, 1080),  # Full HD
        (1366, 768),  # HD
        (1600, 900),  # HD+
        (1280, 1024),  # SXGA
        (1440, 900),  # WXGA+
        (1280, 800),  # WXGA
        (1680, 1050),  # WSXGA+
        (1024, 768)  # XGA
    ]
    r = random.choice(resolutions)
    width, height = r
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    print(f'<<<|{width}x{height}|>>>')
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def add_delay(time_value, delay_value):
    time_format = "%H:%M"
    time_obj = datetime.strptime(time_value, time_format)
    delay_obj = timedelta(minutes=int(delay_value))
    new_time_obj = time_obj + delay_obj
    new_time_value = new_time_obj.strftime(time_format)
    return new_time_value

def extract_delay_value(text):
    match = re.search(r"\+(\d+)", text)
    if match:
        return match.group(1)
    return ""

def get_timetable(driver):
    timetable = {}
    time_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .time")[0:2]
    tag_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .mobile-carrier")[0:2]
    delay_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .time[data-difference]")[0:2]

    for i in range(len(time_elements)):
        time_value = time_elements[i].text
        tag_value = tag_elements[i].text
        if i < len(delay_elements):
            delay_text = delay_elements[i].get_attribute("data-difference")
            delay_value = extract_delay_value(html.unescape(delay_text))

            if not delay_value and any(
                    delay_elements[j].get_attribute("data-difference") for j in range(i + 1, len(delay_elements))):
                continue

            timetable[tag_value] = (time_value, delay_value)
    return timetable

def save_to_database(timetable):
    conn = pymysql.connect(
        host="db4free.net",
        user="crud_maker",
        password="crud_maker",
        database="crud_maker"
    )
    cursor = conn.cursor()
    for tag, time_value in timetable.items():
        delay_value = time_value[1]
        time_with_delays = add_delay(time_value[0], delay_value)
        data_value = datetime.now().strftime("%y/%m/%d")

        query = "INSERT INTO hours (data, train_tag, time) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE time=%s"
        cursor.execute(query, (data_value, tag, time_with_delays, time_with_delays))
        conn.commit()
    cursor.close()
    conn.close()

def print_timetable(timetable):
    global last_timetable
    with open("timetable.txt", "w") as file:
        for tag, time_value in timetable.items():
            delay_value = time_value[1]
            time_with_delays = add_delay(time_value[0], delay_value)
            if delay_value:
                file.write(f'{tag} - {time_value[0]} '
                           f'(+{delay_value}) ='
                           f'{time_with_delays}\n')
                print(f'{Fore.CYAN}{tag}{Fore.RESET} - {time_value[0]} '
                      f'({Fore.RED}+{delay_value}{Fore.RESET}) = '
                      f' {Fore.YELLOW}{time_with_delays}{Fore.RESET}')
            else:
                file.write(f'{tag} - {time_value[0]}\n')
    last_timetable = timetable.copy()

def clear():
    cls = lambda: os.system('cls' if os.name == 'nt' else 'clear');
    cls()


def main():
    driver = configure_driver()
    driver.get("https://bilkom.pl/stacje/tablica")
    from_station_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "fromStation"))
    )

    time.sleep(round(random.uniform(0.50, 2.10), 2))  # anti-anti-bot
    driver.execute_script('window.scrollTo(0, 3)')  # anti-anti-bot

    # Fill the field with "GOGOLIN"
    from_station_input.clear()
    from_station_input.send_keys("GOGOLIN")
    time.sleep(round(random.uniform(2.00, 4.99), 2))  # anti-anti-bot

    # Click the "POKAZ TABLICE" button
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "search-btn"))
    )
    search_button.click()
    time.sleep(round(random.uniform(1.20, 3.99), 2))  # anti-anti-bot

    timetable = get_timetable(driver); driver.quit()
    save_to_database(timetable); print_timetable(timetable)

main()
# no delay since it's more of a shell's script work to do