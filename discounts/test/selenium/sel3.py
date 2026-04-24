from coverage.bytecode import RETURNS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

service = Service(executable_path='../../.venv/chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.get('https://thuvien.ou.edu.vn/')

e = driver.find_element(By.ID, 'txtSearch')
e.send_keys('kiểm thử phần mềm')
e.send_keys(Keys.RETURN)

items = WebDriverWait(driver, 10).until(
    ec.presence_of_all_elements_located((By.CLASS_NAME, 'li-list'))
)

for item in items:
    # print(item.text)
    print(item.find_element(By.CLASS_NAME, 'Titlelink').text)

driver.quit()