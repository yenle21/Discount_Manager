from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import  time

service = Service(executable_path='../../.venv/chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.get('https://vnexpress.net/')

articles = driver.find_elements(By.CSS_SELECTOR, '#automation_TV0 > article')

for article in articles:
    try:
        title = article.find_element(By.TAG_NAME, 'h3')
        des = article.find_element(By.CLASS_NAME, 'description')
        img = article.find_element(By.CSS_SELECTOR, ' div > a > picture > img')
        print(title.text)
        print(des.text)
        print(img.get_attribute('src'))
        print('------------')
    except NoSuchElementException as ex:
        pass

driver.quit()