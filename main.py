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

# List of user agents for anti-bot detection
USER_AGENTS = [
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

LAST_TIMETABLE = None

def configure_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    user_agent = random.choice(USER_AGENTS)
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
    resolution = random.choice(resolutions)
    width, height = resolution
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    print(f'<<<|{width}x{height}|>>>')
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def clear_console():
    clear_command = lambda: os.system('cls' if os.name == 'nt' else 'clear')
    clear_command()


def calculate_delayed_time(base_time, delay_minutes):
    time_format = "%H:%M"
    base_time_obj = datetime.strptime(base_time, time_format)
    delay_obj = timedelta(minutes=int(delay_minutes))
    delayed_time_obj = base_time_obj + delay_obj
    delayed_time = delayed_time_obj.strftime(time_format)
    return delayed_time


def extract_delay_minutes(delay_text):
    match = re.search(r"\+(\d+)", delay_text)
    if match:
        return match.group(1)
    return ""


def get_train_timetable(driver):
    timetable = {}
    time_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .time")[0:5]
    tag_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .mobile-carrier")[0:5]
    delay_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .time[data-difference]")[0:5]

    for i in range(len(time_elements)):
        time_value = time_elements[i].text
        tag_value = tag_elements[i].text
        if i < len(delay_elements):
            delay_text = delay_elements[i].get_attribute("data-difference")
            delay_value = extract_delay_minutes(html.unescape(delay_text))

            if not delay_value and any(
                    delay_elements[j].get_attribute("data-difference") for j in range(i + 1, len(delay_elements))):
                continue

            timetable[tag_value] = (time_value, delay_value)
    return timetable


def save_timetable_to_database(timetable):
    conn = pymysql.connect(
        host="db4free.net",
        user="crud_maker",
        password="crud_maker",
        database="crud_maker"
    )
    cursor = conn.cursor()
    for tag, time_value in timetable.items():
        delay_value = time_value[1]
        time_with_delays = calculate_delayed_time(time_value[0], delay_value)
        data_value = datetime.now().strftime("%y/%m/%d")

        query = "INSERT INTO hours (data, train_tag, time) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE time=%s"
        cursor.execute(query, (data_value, tag, time_with_delays, time_with_delays))
        conn.commit()
    cursor.close()
    conn.close()


def sort_timetable_by_time(timetable):
    sorted_timetable = sorted(timetable.items(), key=lambda x: calculate_delayed_time(x[1][0], x[1][1]))
    return dict(sorted_timetable)


def display_timetable(timetable):
    global LAST_TIMETABLE
    CZAS_FILE_PATH = "/Users/mrarab/Desktop/railway crossing/strona/czas.txt"

    sorted_timetable = sort_timetable_by_time(timetable)

    closest_time = list(sorted_timetable.keys())[0]
    closest_time_value = sorted_timetable[closest_time][0]
    closest_time_delay = sorted_timetable[closest_time][1]
    closest_time_with_delay = calculate_delayed_time(closest_time_value, closest_time_delay)

    print(f'{Fore.CYAN}{closest_time}{Fore.RESET} - {closest_time_value} '
          f'({Fore.RED}+{closest_time_delay}{Fore.RESET}) = {Fore.YELLOW}{closest_time_with_delay}{Fore.RESET}')

    with open(CZAS_FILE_PATH, "w") as czas_file:
        czas_file.write(closest_time_with_delay)  # save to czas.txt

    LAST_TIMETABLE = sorted_timetable.copy()


def main():
    driver = configure_driver()
    driver.get("https://bilkom.pl/stacje/tablica")

    from_station_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "fromStation"))
    )

    time.sleep(round(random.uniform(0.50, 2.10), 2))  # anti-anti-bot
    driver.execute_script('window.scrollTo(0, 3)')  # anti-anti-bot

    from_station_input.clear()
    from_station_input.send_keys("GOGOLIN")
    time.sleep(round(random.uniform(2.00, 4.99), 2))  # anti-anti-bot

    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "search-btn"))
    )
    search_button.click()
    time.sleep(round(random.uniform(1.20, 3.99), 2))  # anti-anti-bot

    timetable = get_train_timetable(driver)
    driver.quit()

    save_timetable_to_database(timetable)
    display_timetable(timetable)

main()