from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import html

driver = webdriver.Chrome()
driver.get("https://bilkom.pl/stacje/tablica")
from_station_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "fromStation"))
)

# filling field with "GOGOLIN"
from_station_input.clear()
from_station_input.send_keys("GOGOLIN")
time.sleep(5)

# pressing button "POKAŻ TABLICE"
search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "search-btn"))
)
search_button.click()
time.sleep(4)

# parse function
def extract_delay_value(text):
    match = re.search(r"\+(\d+)", text)
    if match:
        return match.group(1)
    return ""

# saving times and ICC/R tags
timetable = {}
time_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .time")
tag_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .mobile-carrier")
delay_elements = driver.find_elements(By.CSS_SELECTOR, ".timeTableRow .time[data-difference]")

for i in range(len(time_elements)):
    time_value = time_elements[i].text
    tag_value = tag_elements[i].text
    if i < len(delay_elements):
        delay_text = delay_elements[i].get_attribute("data-difference")
        delay_value = extract_delay_value(html.unescape(delay_text))
    else:
        delay_value = ""
    timetable[tag_value] = (time_value, delay_value)

driver.quit()

# show current times
for tag, time_value in timetable.items():
    delay_value = time_value[1]
    if delay_value:
        print(f'"{tag}" - {time_value[0]}/+{delay_value}')
    else:
        print(f'"{tag}" - {time_value[0]}')
