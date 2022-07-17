from scraper import Scraper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import math
import concurrent.futures
import pandas as pd

class Walmart(Scraper):
    def __init__(self, url):
        super().__init__(url)
        with open('walmart_xpath_dictionary.json') as json_file:
            self.xpaths = json.load(json_file)
        self.laptop_details = None

    def scrape(self):
        try:
            self.driver.get(self.url)
            time.sleep(2)
            urls = self._get_product_urls()
            print(len(urls))
            self._refresh_driver()
        except NoSuchElementException:
            self.driver.get_screenshot_as_file("snapshot_for_debug.png")
            self.solve_captcha()
            self.driver.get(self.url)
            urls = self._get_product_urls()
            self._refresh_driver()
        print(f"{len(urls)} product details to scrape.")
        row_names = ['url', 'name'] + [row_name for row_name in self.xpaths['output'].keys()] + ['scraper_success']
        row_values = []
        for url in urls:
            if len(row_values) != 0:
                row_values.append(self._get_product_details(url))
            else:
                row_values = [self._get_product_details(url)]
            print(f"{len(row_values)*100/len(urls)}% Done", end='\r')
        self.laptop_details = pd.DataFrame(row_values, columns=row_names)
        return self.laptop_details

    def _multi_thread_by_url(self, **kwargs):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            method = kwargs['method']
            urls = kwargs['urls']
            threads = kwargs['threads']
            url_bucket_size = math.ceil(len(urls)/threads)

            futures = []
            for thread in range(threads):
                urls_bucket = [x for x in urls[thread*url_bucket_size:(thread+1)*url_bucket_size]]
                futures.append(executor.submit(method, urls_bucket))

            for future in concurrent.futures.as_completed(futures):
                print(future.result())

    def _get_product_urls(self):
        """
        :return: List of urls of all the products on walmart
        """
        urls = []
        i = 0
        pages = self._get_main_page_urls()
        for page in pages[0:3]:
            try:
                main_elem = self.driver.find_elements_by_xpath(self.xpaths['urls'])
                if len(main_elem) == 0:
                    self.driver.get_screenshot_as_file(f"../output/debug/temp_error_{page}.png")
                    self._refresh_driver()
                    self.driver.get(page)
                    time.sleep(4)
                    main_elem = self.driver.find_elements_by_xpath(self.xpaths['urls'])
                temp_urls = [x.get_attribute("href") for x in main_elem]
                urls = urls + temp_urls
                self._refresh_driver()
                self.driver.get(page)
            except NoSuchElementException:
                self.driver.get_screenshot_as_file(f"../output/debug/error_{page}.png")
                break
            except ElementClickInterceptedException:
                self.driver.get_screenshot_as_file(f"../output/debug/error_{page}.png")
                break
            finally:
                time.sleep(2)
                i += 1
                print(f"Main page {i} product_urls parsed", end="\r")
        return urls

    def _get_main_page_urls(self):
        page_urls = []
        for page in range(26):
            if len(page_urls) == 0:
                page_urls = [self.url + f"?page={page+2}&affinityOverride=default"]
            else:
                page_urls.append(self.url + f"?page={page+2}&affinityOverride=default")
        return page_urls

    def _get_product_details(self, url):
        """
        :param url: url of the product
        :return: product details
        """
        self._refresh_driver()
        try:
            self.driver.get(url)
            name = url.split("/")[-2].replace("-", " ")
            time.sleep(2)
            row = self._get_output()
            self.driver.get_screenshot_as_file(f"../output/scraper_result/success_{name}.png")
            self._refresh_driver()
        except NoSuchElementException:
            self.solve_captcha()
            self.driver.get_screenshot_as_file("../output/debug/snapshot_for_debug.png")
            row = self._get_output()
            self._refresh_driver()
        return [url, name] + list(row.values())

    def _get_output(self):
        output_dict = {}
        output_len = len(self.xpaths['output'].items())
        for element, xpath in self.xpaths['output'].items():
            try:
                output_elem = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                output_dict[element] = output_elem.text
            except NoSuchElementException:
                output_dict[element] = ""
            except TimeoutException:
                output_dict[element] = ""
        scrape_status = [x for x in output_dict.values() if x != ""]
        scrape_success = True if (len(scrape_status) / output_len) >= 0.5 else False
        if not scrape_success:
            self.driver.get_screenshot_as_file(f"../output/debug/parse_error_get_output.png")
        output_dict['scrape_success'] = scrape_success
        return output_dict

    def solve_captcha(self):
        self.driver.maximize_window()
        element = self.driver.find_element_by_css_selector('#px-captcha')
        action = ActionChains(self.driver)
        action.click_and_hold(element)
        action.perform()
        time.sleep(15)
        action.release(element)
        action.perform()
        time.sleep(0.2)
        action.release(element)
        time.sleep(8)