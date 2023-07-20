from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import re
import html
import random
import pymysql
import colorama


# Basic anti-bot detection measures
def configure_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
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
    time_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .time")[0:5]
    tag_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .mobile-carrier")[0:5]
    delay_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .time[data-difference]")[0:5]

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
        data_value = datetime.now().strftime("%d/%m/%y")

        query = "INSERT INTO hours (data, train_tag, time) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE time=%s"
        cursor.execute(query, (data_value, tag, time_with_delays, time_with_delays))
        conn.commit()

    cursor.close()
    conn.close()


def print_timetable(timetable):
    for tag, time_value in timetable.items():
        delay_value = time_value[1]
        time_with_delays = add_delay(time_value[0], delay_value)
        if delay_value:
            print(f'{tag} - {time_value[0]} (+{delay_value}) = {time_with_delays}')
        else:
            print(f'{tag} - {time_value[0]}')


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

    timetable = get_timetable(driver)
    driver.quit()

    save_to_database(timetable)
    print_timetable(timetable)


if __name__ == "__main__":
    main()
