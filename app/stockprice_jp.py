#!/usr/bin/env python

import re
import sys
import os
import json
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

DRIVER_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "chromedriver")

if len(sys.argv) < 2:
    print("stock code is not defined")
    sys.exit(1)

code = sys.argv[1]

if not re.match(r"^[0-9]{4,5}$", code):
    print("stock code is invalid")
    sys.exit(1)

data = {}
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
service = webdriver.chrome.service.Service(executable_path=DRIVER_PATH)

driver = webdriver.Chrome(options=options, service=service)
driver.get("https://www.google.com/finance/quote/{}:TYO?hl=ja".format(code))

try:
    element = driver.find_element(by=By.XPATH, value="//*[@class=\"zzDege\"]")
    data["name"] = element.text
    data["code"] = code
except selenium.common.exceptions.NoSuchElementException as e:
    print(e.msg)
    driver.quit()
    sys.exit(2)


element = driver.find_element(by=By.XPATH, value="//*[@class=\"YMlKec fxKbKc\"]")
data["stock_price"] = element.text.replace("¥", "")

elements = driver.find_elements(by=By.XPATH, value="//*[@class=\"P6K39c\"]")
data["previous_close_price"] = elements[0].text.replace("¥", "")
data["rate_of_dividend"] = elements[5].text
driver.quit()

print(json.dumps(data, ensure_ascii=False))
