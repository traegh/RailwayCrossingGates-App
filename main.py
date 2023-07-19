from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import html
import random
from datetime import datetime, timedelta


def add_delay(time_value, delay_value):
    time_format = "%H:%M"
    time_obj = datetime.strptime(time_value, time_format)
    delay_obj = timedelta(minutes=int(delay_value))
    new_time_obj = time_obj + delay_obj
    new_time_value = new_time_obj.strftime(time_format)
    return new_time_value


driver = webdriver.Chrome()
driver.get("https://bilkom.pl/stacje/tablica")
from_station_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "fromStation"))
)
time.sleep(round(random.uniform(0.50, 2.10), 2))
# filling field with "GOGOLIN"
from_station_input.clear()
from_station_input.send_keys("GOGOLIN")
time.sleep(round(random.uniform(2.00, 4.99), 2))

# pressing button "POKAŻ TABLICE"
search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "search-btn"))
)
search_button.click()
time.sleep(round(random.uniform(1.20, 3.99), 2))


def extract_delay_value(text):
    match = re.search(r"\+(\d+)", text)
    if match:
        return match.group(1)
    return ""

# saving times and ICC/R tags
timetable = {}
time_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .time")[0:4]
tag_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .mobile-carrier")[0:4]
delay_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .time[data-difference]")[0:4]

for i in range(len(time_elements)):
    time_value = time_elements[i].text; print(f'time_value={time_value}')
    tag_value = tag_elements[i].text
    if i < len(delay_elements):
        delay_text = delay_elements[i].get_attribute("data-difference")
        delay_value = extract_delay_value(html.unescape(delay_text)); print(f'delay_value={delay_value}')

        # Sprawdź, czy delay_value jest puste i czy istnieje inny czas z delay_value
        if not delay_value and any(
                delay_elements[j].get_attribute("data-difference") for j in range(i + 1, len(delay_elements))):
            continue  # Pomijamy ten czas, który nie ma łatki opóźnienia i istnieje inny czas z łatką opóźnienia

        new_time_value = add_delay(time_value, delay_value)
    else:
        delay_value = ""
        new_time_value = time_value
    timetable[tag_value] = (new_time_value, delay_value)

driver.quit(); print("\n- - -\n")
for tag, time_value in timetable.items():
    print(f'[{tag}] {time_value[0]} // {time_value[1]}')
