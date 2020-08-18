#!/usr/bin/python3
import bs4 as bs
import requests
import random
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import sys

#randomize user agent
def GET_UA():
    uastrings = [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
                ]
 
    return random.choice(uastrings)

def scrape(name, model, driver, dictOfPrices):

    #Best Buy
    try:
        BBUrl = 'https://www.bestbuy.com/site/searchpage.jsp?st=' + name.replace(" ", "+") + "+" + model + '&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys'
        driver.get(BBUrl)
        price = driver.find_element(By.XPATH, '//*[@class="sku-item-list"]').find_element(By.XPATH, '//*[@class="sku-item"]').find_element(By.XPATH, '//*[@class="priceView-hero-price priceView-customer-price"]').find_elements_by_tag_name('span')[0].text
        if model in dictOfPrices:
            dictOfPrices[model].append({"Best Buy" : price})
        else:
            dictOfPrices[model] = [{"Best Buy" : price}]
    except Exception:
        if model in dictOfPrices:
            dictOfPrices[model].append({"Best Buy" : "Price could not be found"})
        else:
            dictOfPrices[model] = [{"Best Buy" : "Price could not be found"}]
       
    #Amazon
    try:
        AUrl = "https://www.amazon.com/s?k=" + name.replace(" ", "+") + "+" + model + "&ref=nb_sb_noss"
        driver.get(AUrl)      
        price = ''
        for i in range(0, 10):
            query_string = '//*[@data-index="' + str(i) + '"]'
            item = driver.find_element(By.XPATH, query_string)
            classVar = item.get_attribute("class")
            if("AdHolder" in classVar or "a-section" in classVar):
                continue
            else:
                try:
                    price = '$' + item.find_elements_by_class_name("a-price-whole")[0].text + "." + driver.find_elements_by_class_name("a-price-fraction")[0].text
                except:
                    try:
                        price = item.find_elements_by_class_name("a-offscreen")[0].text
                    except:
                        driver.find_element_by_class_name("a-link-normal.a-text-normal").click()
                        price = driver.find_element_by_id("price_inside_buybox").text
                break
            
        if model in dictOfPrices:
            dictOfPrices[model].append({"Amazon" : price})
        else:
            dictOfPrices[model] = [{"Amazon" : price}]
    except: 
        if model in dictOfPrices:
            dictOfPrices[model].append({"Amazon" : "Price could not be found"})
        else:
            dictOfPrices[model] = [{"Amazon" : "Price could not be found"}]

    #Walmart
    try:
        WUrl = "https://www.walmart.com/search/?query=" + name.replace(" ", "%20")
        driver.implicitly_wait(0)
        driver.get(WUrl)
        price = driver.find_element(By.XPATH, '//*[@class="search-product-result"]')
        try:
            price = price.find_element(By.XPATH, '//*[@data-tl-id="ProductTileListView-0"]')
        except:
            price = price.find_element(By.XPATH, '//*[@data-tl-id="ProductTileGridView-0"]')
        price = price.find_element_by_xpath('//*[@class="price display-inline-block arrange-fit price price-main"]').find_elements_by_tag_name('span')[1].text
        if model in dictOfPrices:
            dictOfPrices[model].append({"Walmart" : price})
        else:
            dictOfPrices[model] = [{"Walmart" : price}]
    except Exception:
        if model in dictOfPrices:
            dictOfPrices[model].append({"Walmart" : "Price could not be found"})
        else:
            dictOfPrices[model] = [{"Walmart" : "Price could not be found"}]
            
    #Target
    try:
        TUrl = "https://www.target.com/s?searchTerm=" + name.replace(" ", "+")
        driver.implicitly_wait(3)
        driver.get(TUrl)
        driver.find_element(By.XPATH, '//*[@data-test="product-title"]').click()
        price = driver.find_element(By.XPATH, '//*[@data-test="product-price"]').text
        if model in dictOfPrices:
            dictOfPrices[model].append({"Target" : price})
        else:
            dictOfPrices[model] = [{"Target" : price}]
    except Exception:
        if model in dictOfPrices:
            dictOfPrices[model].append({"Target" : "Price could not be found"})
        else:
            dictOfPrices[model] = [{"Target" : "Price could not be found"}]
    
opt = Options()
opt.add_argument("--headless")
opt.add_argument("user-agent=" + GET_UA())
driver = webdriver.Chrome(options = opt)
results = {}
input = json.load(sys.stdin)
name = input["Product"]
model = input["Model"]
scrape(name, model, driver, results)
driver.close()
driver.quit()
print("Content-Type: text/html")
print ("")
print("<body>")
print(json.dumps(results))
print("</body>")