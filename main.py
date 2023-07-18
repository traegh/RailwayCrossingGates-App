from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Inicjalizacja przeglądarki
driver = webdriver.Chrome()
driver.get("https://bilkom.pl/stacje/tablica")

# Wyszukanie pola wprowadzania frazy
from_station_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "fromStation"))
)

# Wpisanie frazy "GOGOLIN"
from_station_input.clear()
from_station_input.send_keys("GOGOLIN")
time.sleep(5)


# Kliknięcie przycisku "POKAŻ TABLICE"
search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "search-btn"))
)
search_button.click()

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "result-element-id"))
)
