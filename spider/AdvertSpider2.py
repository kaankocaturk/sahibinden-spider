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
import json, random
import re


root_dir= "./downloads"

user_agents = [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 OPR/76.0.4017.123",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 OPR/75.0.3969.243",
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 OPR/75.0.3969.93",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 OPR/74.0.3911.160",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36 OPR/74.0.3911.154",
   ]


class AdvertSpider(scrapy.Spider):
   name = "advert2"
  # start_urls = [
  #     "https://www.sahibinden.com/ilan/vasita-otomobil-toyota-beyaz-melek-1996-gli-toyota-corollo-klimali-4-cam-otomatik-hid-1174973401/detay",
  # ]
   root_url = "https://www.sahibinden.com"
   imgUrls = []
   counter = 1


   def __init__(self, urlsfile=None, *args, **kwargs):
       super(AdvertSpider, self).__init__(*args, **kwargs)


       if urlsfile:
           with open(urlsfile,'r') as file:
               data = json.load(file)

               urls = data.get("advert_urls_set",[] )
               #urls = data.get("sample_set",[] )

               # filter urls if before downloaded images from it
               filtered_urls = self.filterOutDownloadedUrls(urls)


               #filtered_urls = [self.root_url + url for url in filtered_urls]
               google_urls = []
               for url in filtered_urls:
                    pattern = r"-([0-9]+)/detay"
                    advert_code = re.search(pattern, url).group(1)
                    google_url = "https://www.google.com/search?q=" + advert_code + "+sahibinden"
                    google_urls.append(google_url)
               print("google_urls: {} ".format(google_urls))

               self.start_urls = google_urls

       else:
           self.start_urls=[]
       user_agent = random.choice(user_agents)


       firefox_options = webdriver.FirefoxOptions()
       firefox_options.set_preference("detach", True)  # This may not have the same effect as Chrome's detach, but we'll set some equivalent options
       firefox_options.set_preference("general.useragent.override", user_agent)
       firefox_options.set_preference("dom.webdriver.enabled", False)
       firefox_options.set_preference('useAutomationExtension', False)
       firefox_options.set_preference("webdriver.load.strategy", "unstable")


       self.driver = webdriver.Firefox(options=firefox_options)
       self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
  
  # def start_requets(self):
  #     for url in self.urls:
  #         yield scrapy.Request(url=url, callback=self.parse)
   def parse(self, response):
       self.resetImgUrl()
       self.driver.get(response.url)
       self.openAdvertPage()


       try :
           if self.counter == 1 :
                #time.sleep(2)
                #self.passHumanTest()
                pass
           self.counter = self.counter + 1
           #time.sleep(5)




           if "login" in self.driver.current_url:
               self.logger.info("Redirected to login page, trying to bypass")
               #self.driver.back()


       except Exception as e:
           self.logger.error("Error while redirecting: {}".format(e))
           self.closed()               


       try :
           
          
           time.sleep(5)
           advert_code = self.extractAdvertCode(response.url)
           if not advert_code in self.driver.current_url :
               self.logger.info("Advert removed, moving next advert")
               #self.driver.get(response.url)
               return

          # self.handleLowLevelImages(response.url)
           self.handleHighLevelImages(self.driver.current_url)


           print("imgUrls: {}".format(self.imgUrls))
           print("current_url: {}".format(self.driver.current_url))
           print("response.url: {}".format(response.url))

           self.extractAdvertCode(self.driver.current_url, r"([0-9]+)/detay")
           self.fetch_and_save_images(self.imgUrls, self.advert_dir)
       except Exception as e:
           self.logger.error("Error while parsing: {}".format(e))
           self.closed()
  
   def closed(self, reason):
        self.driver.quit()
    
   def openAdvertPage(self) :
        xpath = '//*[@class="LC20lb MBeuO DKV0Md"]'
        self.clickElement(xpath)
        #adverrt_element = self.driver.find_element(By.CLASS_NAME, "LC20lb MBeuO DKV0Md")



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


           # Locate the input element within the label and click it
           input_element = label_element.find_element(By.TAG_NAME, "input")
           input_element.click()
           print("Input element clicked")


       except Exception as e:
           self.logger.error("Error while locating and clicking the input element: {}".format(e))
           self.driver.quit()
           return
  
   def waitUntilImageContainerFound(self, url):
       try:
           element_clickable = False
           while not element_clickable:
               try:
                   element = self.driver.find_element(By.XPATH, '//*[@class="classifiedDetailThumbList "]')
                  
                   if element.is_displayed() and element.is_enabled():  # Check if the element is both displayed and enabled
                       element_clickable = True
                   time.sleep(2)
               except Exception as e:
                   print("element not found:{} ".format(url))
                   time.sleep(1)
           time.sleep(2)  # Allow additional time for page components to load completely
       except Exception as e:
           self.logger.error("Error while waiting for page elements: {}".format(e))
           self.driver.quit()
           return
  
   def handleImgUrls(self):
       response = Selector(text=self.driver.page_source)
       img_elements = response.xpath('//*[@class="classifiedDetailThumbList "]//li//img')
       try:
           [self.setImgUrl(src) for src in img_elements.xpath('@src').extract()]
       except Exception as e:
           print("parsing error: {}".format(e))


   def setImgUrl(self, url):
       self.imgUrls.append(url)

   def resetImgUrl(self):
       self.imgUrls = []


  
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
  
   def extractAdvertCode(self, url, pattern =  r"([0-9]+)"):
       print("urlurl: {}".format(type(url)))
       print("urlurl: {}".format(pattern))

       advert_code = re.search(pattern, url)
       print("urlurl: {}".format(advert_code))


       if advert_code:
           self.advert_dir = root_dir + "/" + advert_code.group(1)
           return advert_code.group(1)
       else :
           print("advert code not found while parsing url: {}".format(url))
           self.closed()


   def filterOutDownloadedUrls(self, urls):
       download_folder = os.path.expanduser("./downloads")
       filenames =[file for file in os.listdir(download_folder)]

       filtered_urls =[url for url in urls if(not any(filename in url for filename in filenames))]


       print("filtered_urls: {}".format(filtered_urls))




       return filtered_urls
   
   def isAdvertDownloaded(self, advert_code):
       download_folder = os.path.expanduser(root_dir)
       filenames =[file for file in os.listdir(download_folder)]

       return advert_code in filenames

  


   def handleLowLevelImages(self, url ):
       self.waitUntilImageContainerFound(url)
       self.handleImgUrls()


   def handleHighLevelImages(self, url ):
        # TODO check if it is downloaded before then return
        advert_code = self.extractAdvertCode(url)
        if self.isAdvertDownloaded(advert_code) :
            self.logger("Advert {} downloaded before. Stopping downloading images".format(advert_code))
            return
        print("handleHighLevelImages")
       
        self.waitUntilImageContainerFound(url)
        self.openHighImages()

        counter =  self.getHighImageNumber()

        xpath = '//*[@class="megaPhotoRight"]'
        while counter >= 1:
            counter= counter-1
            self.handleHighImgUrl()
            self.clickElement(xpath)

   def getHighImageNumber(self):
        pattern = r"([0-9]+)"
        
        span_element = self.driver.find_element(By.CLASS_NAME, 'images-count')

        # Extract the text from the span element
        value = span_element.text.split('/')[1]
        value = re.search(pattern, value).group(1)

        print("getHighImageNumber: {} ".format(value))

        return int(value)
  
   def openHighImages(self):
       try :
           element = self.driver.find_element(By.XPATH, '//*[@id="mega-foto"]')
           element.click()
           time.sleep(2)
   
       except Exception as e:
           print("mega-foto button not found:{} ".format(e))
           self.closed()
        
        # wait for loading of image
       xpath = '//*[@class="loader"]'
       flag = True
       while flag:
           element = self.driver.find_element(By.XPATH, xpath)
           display = element.get_attribute("display") 
           print("mega-foto element:{} ".format(type(display))) 
           print("mega-foto element:{} ".format(display == None)) 
           if display is None : 
               flag = False
           time.sleep(10)
            
           

   def clickElement(self, xpath):
        flag= True
        while flag : 
            if self.is_element_clickable(xpath):
                element = self.driver.find_element(By.XPATH, xpath)
                element.click()
                flag = False
                return
            time.sleep(2)

   def handleHighImgUrl(self):
       print("handleHighImgUrl")


       response = Selector(text=self.driver.page_source)
       not_found = True
       while not_found:
        time.sleep(2)
        img_elements = response.xpath('//*[@class="mega-photo-img"]//img')
        print("handleHighImgUrl: {}".format(img_elements))
        if len(img_elements) > 0 :
            not_found = False

       try:
           src =  img_elements[0].xpath('@src').extract()
           self.setImgUrl(src[0])
       except Exception as e:
           print("parsing error: {}".format(e))

   def is_element_clickable(self, xpath):
        try:
            wait = WebDriverWait(self.driver, 1)  # Short wait to quickly determine clickability
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            return True
        except Exception as e:
            return False














  

