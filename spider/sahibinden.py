import scrapy

from selenium import webdriver
from scrapy.spiders import Spider
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os
import json

class SahibindenSpider(scrapy.Spider):
    name = "sahibinden"
    start_urls = [
        "http://www.sahibinden.com/otomobil/sahibinden",
    ]
    advertUrls = []
    current_page=2

    def __init__(self, *args, **kwargs):
        super(SahibindenSpider, self).__init__(*args, **kwargs)

        firefox_options = webdriver.FirefoxOptions()
        firefox_options.set_preference("detach", True)  # This may not have the same effect as Chrome's detach, but we'll set some equivalent options

        self.driver = webdriver.Firefox(options=firefox_options)

    def parse(self, response):

        self.driver.get(response.url)
        
        if(self.current_page==2):
            self.passHumanTest()

        self.waitUntilCarContainerFound()

        self.handleAdvertUrls()
        self.update_advert_urls(self.advertUrls)
        #print("advertUrls: {}".format(self.advertUrls))
        print("advertUrls: {}".format(len(self.advertUrls)))

        #yield response.follow("https://www.sahibinden.com/otomobil/sahibinden?pagingOffset=20", callback=self.parse)
        try :
             # Follow the next page link if it exists
            #next_page_url = self.driver.find_element(By.CSS_SELECTOR, f'ul.pageNaviButtons li a[title="{self.current_page}"]').get_attribute("href")
            next_page_url = f'https://www.sahibinden.com/otomobil/sahibinden?pagingOffset={(self.current_page*20)-20}'
            print("next_page: {}".format(next_page_url))

            if next_page_url:
                self.current_page = self.current_page +1
                yield response.follow(next_page_url, callback=self.parse)
            else : 
                self.closed()
        except Exception as e: 
            self.logger.error("Error while uploading next page : {}".format(e))
            self.closed()

    def closed(self, reason):
        self.driver.quit()
    
    def passHumanTest(self):
        try:
            # Wait for the iframe to be present and switch to it
            iframe = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
            )
            self.driver.switch_to.frame(iframe)

            # Wait until the label element with class "cb-lb" is present
            label_element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "label.cb-lb"))
            )
            print("label_element: {} ".format(label_element))

            # Locate the input element within the label and click it
            input_element = label_element.find_element(By.TAG_NAME, "input")
            input_element.click()
            print("Input element clicked")

        except Exception as e:
            self.logger.error("Error while locating and clicking the input element: {}".format(e))
            self.driver.quit()
            return
    
    def waitUntilCarContainerFound(self):
        try:
            element_clickable = False
            while not element_clickable:
                try:
                    element = self.driver.find_element(By.XPATH, '//*[@id="searchResultsTable"]')
                    
                    if element.is_displayed() and element.is_enabled():  # Check if the element is both displayed and enabled
                        element_clickable = True
                        self.logger.info("element found")

                    time.sleep(2)
                except Exception as e:
                    self.logger.warning("element not found")
                    time.sleep(1)
            time.sleep(2)  # Allow additional time for page components to load completely
        except Exception as e:
            self.logger.error("Error while waiting for page elements: {}".format(e))
            self.driver.quit()
            return
    
    def handleAdvertUrls(self):
        try: 
            response = Selector(text=self.driver.page_source)


            # Fetch the a elements under the element with id "searchResultsTable"
            a_elements = response.css('#searchResultsTable  a')
    
            # Extract the href attribute of each a element
            hrefs = a_elements.xpath('@href').extract()
            a_hrefs = response.css('#searchResultsTable .searchResultsTitleValue   a::attr(href)').getall()
            print("a_hrefs: {}".format(a_hrefs))

            for href in a_hrefs:
                if "ilan" in href:
                    self.setAdvertUrls(href)

        except Exception as e:
            self.logger.error("parsing error: {}".format(e))

    def setAdvertUrls(self, url):
        self.advertUrls.append(url)

    
    def fetch_and_save_images(self, urls, save_directory):
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        for i, url in enumerate(urls):
            try:
                response = requests.get(url)
                response.raise_for_status()  # Check if the request was successful
                file_name = os.path.join(save_directory, f'image_{i + 1}.jpg')  # Save as image_1.jpg, image_2.jpg, etc.
                with open(file_name, 'wb') as file:
                    file.write(response.content)
                print(f"Image saved: {file_name}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {url}: {e}")
    
    def update_advert_urls(self, new_urls) :
        # Step 1: Read the JSON file into a Python dictionary
        with open('data.json', 'r') as file:
            data = json.load(file)

        # Step 2: Update the string array in the dictionary
        data['advert_urls'] = new_urls

        # Step 3: Write the updated dictionary back to the JSON file
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)

        print("JSON file updated successfully.")



    