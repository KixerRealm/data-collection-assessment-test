import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0")

driver = webdriver.Chrome(options=options)


products_list = []
visited_links = set()

for i in range(1, 20):
    search_url = f"https://www.newegg.com/p/pl?d=graphics+card&page={i}"
    driver.get(search_url)
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item-cell a.item-title")))

    try:
        product_elements = driver.find_elements(By.CSS_SELECTOR, ".item-cell a.item-title")
        for element in product_elements:
            link = element.get_attribute("href")
            if link and "newegg.com" in link and link not in visited_links:
                visited_links.add(link)
                products_list.append(link)
                if len(products_list) >= 500:
                    break
        if len(products_list) >= 500:
            break
    except Exception as e:
        print(e)

print(len(products_list))

full_products = []

def safe_find_text(by, selector):
    try:
        return driver.find_element(by, selector).text.strip()
    except NoSuchElementException:
        return "N/A"

for product in products_list:
    driver.get(product)
    time.sleep(random.uniform(1.5, 3.0))

    title = safe_find_text(By.CLASS_NAME, "product-title")

    try:
        description = driver.find_element(By.CLASS_NAME, "product-bullets").text.strip().replace("\n", ", ")
    except NoSuchElementException:
        description = "N/A"

    try:
        price_container = driver.find_element(By.CSS_SELECTOR, "div.price-current")
        strong = price_container.find_element(By.TAG_NAME, "strong").text.strip()
        sup = price_container.find_element(By.TAG_NAME, "sup").text.strip()
        price = f"${strong}{sup}"
    except NoSuchElementException:
        price = "N/A"

    try:
        rating_tag = driver.find_element(By.CSS_SELECTOR, "i.rating[title]")
        rating = rating_tag.get_attribute("title").strip()
    except NoSuchElementException:
        rating = "N/A"

    seller = safe_find_text(By.CSS_SELECTOR, "div.product-seller-sold-by").replace("Sold by", "").strip()

    p = {
        'Title': title,
        'Description': description,
        'Price': price,
        'Rating': rating,
        'Seller': seller
    }
    print(p)
    full_products.append(p)

driver.quit()
print(len(full_products))

df = pd.DataFrame(full_products)
df.to_csv("newegg.csv", index=False)