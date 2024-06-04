# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random
import time
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from scrapy import signals
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class TutorialSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 OPR/76.0.4017.123",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 OPR/75.0.3969.243",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 OPR/75.0.3969.93",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 OPR/74.0.3911.160",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36 OPR/74.0.3911.154",
    ]
    
    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent

        #return request


    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class SeleniumMiddleware:
    def __init__(self):
        self.driver = None

    def process_request(self, request, spider):
        spider.logger.info("Processing request with SeleniumMiddleware: {}".format(request.url) )

        user_agent = request.headers.get('User-Agent', '').decode('utf-8')

        firefox_options = webdriver.FirefoxOptions()
        firefox_options.set_preference("detach", True)  # This may not have the same effect as Chrome's detach, but we'll set some equivalent options

        firefox_options.set_preference("general.useragent.override", user_agent)

        if self.driver is None:
            self.driver = webdriver.Firefox(options=firefox_options)

            spider.logger.info("WebDriver initialized")
        self.driver.get(request.url)
        time.sleep(10)
        if(request.url != self.driver.current_url):
            #print("request.url::: {}".format(request.url ))
            #print("self.driver.current_url::: {}".format(self.driver.current_url ))

            self.passHumanTest(spider)

        body = self.driver.page_source

        response = HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)
        print("requestttt::: {}".format(request.url ))

        response.meta.update(request.meta)
        response.meta['driver'] = self.driver
        print("responseeeee::: {}".format(response.meta ))
        #print("responseeeee::: {}".format(response.meta.driver ))

        time.sleep(10)

        return response

    def __del__(self, spider):
        if self.driver:
            self.driver.quit()
            spider.logger.info("WebDriver closed")

    def passHumanTest(self,spider):
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
            print("Are You Robot element clicked")

        except Exception as e:
            spider.logger.error("Error while locating and clicking the input element: {}".format(e))
            self.driver.quit()
            return
