#!/usr/bin/env python

import re
import time
import sys
import os
import json
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DRIVER_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "chromedriver")

INDUSTRY_CODES = [
    {"min": 1301, "max": 1399, "description": "水産・農林業"},
    {"min": 1401, "max": 1499, "description": "建設業"},
    {"min": 1501, "max": 1599, "description": "鉱業"},
    {"min": 1601, "max": 1699, "description": "鉱業（石油・ガス開発）"},
    {"min": 1701, "max": 1999, "description": "建設業"},
    {"min": 2001, "max": 2999, "description": "食料品"},
    {"min": 3001, "max": 3499, "description": "繊維製品"},
    {"min": 3501, "max": 3699, "description": "繊維製品"},
    {"min": 3701, "max": 3999, "description": "パルプ・紙"},
    {"min": 4001, "max": 4999, "description": "化学・医薬品"},
    {"min": 5001, "max": 5099, "description": "石油・石炭製品"},
    {"min": 5101, "max": 5199, "description": "ゴム製品"},
    {"min": 5201, "max": 5399, "description": "ガラス・土石製品"},
    {"min": 5401, "max": 5699, "description": "鉄鋼"},
    {"min": 5701, "max": 5899, "description": "非鉄金属"},
    {"min": 5901, "max": 5999, "description": "金属製品"},
    {"min": 6001, "max": 6499, "description": "機械"},
    {"min": 6501, "max": 6999, "description": "電気機器"},
    {"min": 7001, "max": 7499, "description": "輸送用機器"},
    {"min": 7701, "max": 7799, "description": "精密機器"},
    {"min": 7801, "max": 7999, "description": "その他製品"},
    {"min": 8001, "max": 8299, "description": "卸売業"},
    {"min": 8301, "max": 8599, "description": "銀行・その他金融"},
    {"min": 8601, "max": 8699, "description": "証券・先物取引業"},
    {"min": 8701, "max": 8799, "description": "保険"},
    {"min": 8801, "max": 8899, "description": "不動産"},
    {"min": 9001, "max": 9099, "description": "陸運"},
    {"min": 9101, "max": 9199, "description": "海運"},
    {"min": 9201, "max": 9299, "description": "空運"},
    {"min": 9301, "max": 9399, "description": "倉庫・運輸関連"},
    {"min": 9401, "max": 9499, "description": "情報通信"},
    {"min": 9501, "max": 9599, "description": "電気ガス"},
    {"min": 9601, "max": 9999, "description": "サービス業"}
]

def get_industry_name_by_code(code):

    for entry in INDUSTRY_CODES:
        if entry["min"] <= code and entry["max"] >= code:
            return entry["description"]

    return "サービス業"

def jpnumstr2int(s):

    s = s.replace("¥", "")
    s = s.replace(",", "")
    if re.match(r"^.*兆$", s):
        s = float(s.replace("兆", "")) * 1000000000000
    elif re.match(r"^.*億$", s):
        s = float(s.replace("億", "")) * 100000000
    elif re.match(r"^.*万$", s):
        s = float(s.replace("万", "")) * 10000
    else:
        s = float(s)
    return s

if len(sys.argv) < 2:
    print("stock code is not defined")
    sys.exit(1)

code = sys.argv[1]

if not re.match(r"^[0-9]{4,5}$", code):
    print("stock code is invalid")
    sys.exit(1)

code = int(code)

data = {}
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
service = webdriver.chrome.service.Service(executable_path=DRIVER_PATH)

driver = webdriver.Chrome(options=options, service=service)
#driver.implicitly_wait(5)
#WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located)
driver.get("https://www.google.com/finance/quote/{}:TYO?hl=ja".format(code))

try:
    element = driver.find_element(by=By.XPATH, value="//*[@class=\"zzDege\"]")
    data["name"]          = element.text
    data["code"]          = code
    data["industry_name"] = get_industry_name_by_code(code)
except selenium.common.exceptions.NoSuchElementException as e:
    print(e.msg, file=sys.stderr)
    driver.quit()
    sys.exit(1)


# 株価
element = driver.find_element(by=By.XPATH, value="//*[@class=\"YMlKec fxKbKc\"]")
stock_price = jpnumstr2int(element.text)
data["stock_price"] = stock_price

# 前日終値
elements = driver.find_elements(by=By.XPATH, value="//*[@class=\"P6K39c\"]")
previous_close_price = jpnumstr2int(elements[0].text)
data["previous_close_price"] = previous_close_price

# PER
per = elements[4].text
if per == "-":
    data["per"] = 0
else:
    data["per"] = round(float(per), 2)

# 配当利回り
if elements[5].text == "-":
    rate_of_dividend = 0
else:
    rate_of_dividend = elements[5].text.replace("%", "")
    rate_of_dividend = round(float(rate_of_dividend) / 100, 4)
data["rate_of_dividend"] = rate_of_dividend

# open balance sheet
try:
    element = driver.find_element(by=By.XPATH, value="//span[text()=\"貸借対照表\"]")
    element.click()
    element = None
    time.sleep(3)

    elements = driver.find_elements(by=By.XPATH, value="//*[@class=\"QXDnM\"]")

    # 純資産
    net_assets= jpnumstr2int(elements[10].text)
    # 発行済み株式枚数
    outstanding_shares = jpnumstr2int(elements[11].text)
    elements = None

    bps = round(net_assets / outstanding_shares, 2)
    pbr = round(stock_price / bps, 2)

except selenium.common.exceptions.NoSuchElementException as e:
    print(e.msg, file=sys.stderr)
    bps = 0
    pbr = 0


data["bps"] = bps
data["pbr"] = pbr
driver.quit()

print(json.dumps(data, ensure_ascii=False))
