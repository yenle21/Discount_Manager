from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

service = Service(executable_path='../../.venv/chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.get('https://tiki.vn/dien-thoai-may-tinh-bang/c1789')

driver.execute_script('window.scrollTo(0, 300)')
driver.implicitly_wait(3)

products = driver.find_elements(By.CLASS_NAME, 'product-item')
pages = []
for p in products[:3]:
    print(p.get_attribute('href'))
    pages.append(p.get_attribute('href'))

    title = p.find_element(By.CSS_SELECTOR, 'div.content div.info h3')
    print(title.text)
    print('---------------------')

print("==============================")

for idx, p in enumerate(pages):
    print(p)
    driver.get(p)
    driver.save_screenshot(f'test{idx}.png')
    driver.execute_script('window.scrollTo(0, 2000)')
    driver.execute_script('window.scrollTo(0, 1000)')
    driver.execute_script('window.scrollTo(0, 3000)')

    comments = driver.find_elements(By.CSS_SELECTOR, '.customer-reviews div.review-comment__content')
    for c in comments:
        print(c.text)
    print('---------------------')

driver.quit()