import scrapy
import time
from scrapy.http import Request
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from twilio.rest import Client
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

client = Client("Twilioemail", "Twilio password")# add info here for twilio account


class NeweggSpider(scrapy.Spider):
    name = "newegg"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/43.0.2357.130 Safari/537.36 "

    def __init__(self, *args, **kwargs):
        options = Options()
        options.headless = True
        self.profile = webdriver.FirefoxProfile(
            r'mozilla profile') #mozilla profile
        self.driver = webdriver.Firefox(self.profile, options=options, executable_path=GeckoDriverManager().install())
        self.wait = WebDriverWait(self.driver, 5)
        self.products = []
        self.start_urls = ["https://www.newegg.com/p/pl?d=3080&N=100007709%204841%2050001314%204021%2050001315%2050001312%2050001402&isdeptsrh=1", ]# Link for product, this is 3080 with some presets

    def parse(self, response, *args, **kwargs):
        url = 'https://www.newegg.com/p/pl?d=3080&N=100007709%204841%2050001314%204021%2050001315%2050001312%2050001402&isdeptsrh=1'#same link again
        self.driver.get(url)
        # Finding Product Availability.
        try:
            self.products = []
            self.products = self.driver.find_element_by_xpath("//*[@class='btn btn-primary btn-mini']").text.strip()
            print("\nProduct is Available.\n")
            if len(self.products):
                for product in self.products:
                    # Starting Bot. (Page 1)
                    print("\nFound 1 item to add to cart.\n")
                    self.wait.until(
                        EC.visibility_of_element_located((By.XPATH, "//*[@class='btn btn-primary btn-mini']")))
                    time.sleep(.5)
                    self.driver.find_element_by_xpath("//*[@class='btn btn-primary btn-mini']").click()
                    time.sleep(.5)
                    break
        except (AttributeError, NoSuchElementException, WebDriverException, TimeoutException) as error:
            if error:
                print("\nProduct Sold Out: Retrying in 3 Seconds.\n")
                time.sleep(3)
                yield Request(url, callback=self.parse, dont_filter=True)

        if len(self.products):
            # Going to Check Out Page. (Page 2)
            print("\nGoing to Checkout Cart. (Page 2)\n")
            self.driver.get("https://secure.newegg.com/Shopping/ShoppingCart.aspx?Submit=view")#cart
            try:
                print("\nClicking Secure Checkout. (Page 2)\n")
                available = self.driver.find_element_by_xpath("//*[@class='btn btn-primary btn-wide']").is_enabled()
                if available:
                    time.sleep(1)
                    self.driver.find_element_by_xpath("//*[@class='btn btn-primary btn-wide']").click()
            except (AttributeError, NoSuchElementException, WebDriverException, TimeoutException) as error:
                if error:
                    print("\nSecuring Checkout button is not Clickable.\n")
                    time.sleep(3)
                    yield Request(url, callback=self.parse, dont_filter=True)

            # Login Password. (Page 3)
            # try:
            #     print("\nAttempting Password. (Page 3)\n")
            #     self.wait.until(EC.visibility_of_element_located((By.ID, "labeled-input-password")))
            #     password = self.driver.find_element_by_id("labeled-input-password")
            #     password.send_keys("###") # NEWEGG PASSWORD HERE
            #     password.send_keys(Keys.ENTER)
            # except (AttributeError, NoSuchElementException, WebDriverException, TimeoutException) as error:
            #     if error:
            #         print("\nDid Not Use Password. (Page 3)\n")
            try:
                print("\nMoving on with payment (Page 3)\n")
                test123 = self.driver.find_element_by_xpath("//*[@class='btn btn-primary checkout-step-action-done layout-quarter']").is_enabled()
                if test123:
                    time.sleep(1)
                    self.driver.find_element_by_xpath("//*[@class='btn btn-primary checkout-step-action-done layout-quarter']").click()
            except (AttributeError, NoSuchElementException, WebDriverException, TimeoutException) as error:
                if error:
                    print("\nNot WORKING\n")
                    time.sleep(3)
                    yield Request(url, callback=self.parse, dont_filter=True)
            # Submit CVV Code(Must type CVV number. (Page 4)
            try:
                print("\nTrying Credit Card CVV Number. (Page 4)\n")
                self.wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "//input[@class='form-text mask-cvv-4'][@type='text']")))
                security_code = self.driver.find_element_by_xpath(
                    "//input[@class='form-text mask-cvv-4'][@type='text']")
                time.sleep(1)
                security_code.send_keys(
                    Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + "###")  # You can enter your CVV number here.!!!!!!!!!
            except (AttributeError, NoSuchElementException, WebDriverException, TimeoutException) as error:
                if error:
                    print("\nCould Not Type CVV. (Page 4)\n")

            # ARE YOU READY TO BUY? (Page 4) COMMENT BELOW OUT IF YOU DONT WANT IT TO BUY STUFF


            try:
                print("\nBuying Product. (Page 4)\n")
                time.sleep(.5)
                final_step = self.driver.find_element_by_id("btnCreditCard").is_enabled()
                if final_step:
                    print("\nFinalizing Bot!...\n")
                    self.driver.find_element_by_id("btnCreditCard").click()
                    time.sleep(5)
                    print("\nBot has Completed Checkout.\n")
                    # Want to Receive Text Messages?
                    client.messages.create(to="+1your number", from_="+1twilio number",
                                           body="Bot made a Purchase. newegg !")
            except (AttributeError, NoSuchElementException, WebDriverException, TimeoutException) as error:
                if error:
                    print("\nRestarting: Checkout Did Not Go Through. (Page 4)\n")
                    time.sleep(3)
                    yield Request(url, callback=self.parse, dont_filter=True)

