import time
from selenium import webdriver
from selenium_stealth import stealth

class Scraper:
    def __init__(self, url=None):
        self.url = url
        self.driver = webdriver.Chrome(options=self._get_options())
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

    def _get_options(self):
        # PROXY_STR = "111.222.111.222:1234"
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--incognito")
        # options.add_argument('--proxy-server=%s' % PROXY_STR)
        options.add_argument("user-agent=THis")
        options.add_argument("--headless")
        options.add_argument("disk-cache-size=0")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return options

    def _refresh_driver(self):
        self.driver.delete_all_cookies()
        self.driver.quit()
        self.driver = webdriver.Chrome(options=self._get_options())
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        time.sleep(2)

    def send_input(self):
        pass

    def scrape(self):
        pass

    def _get_output(self):
        pass

    def bypass_captcha(self):
        pass

    def trigger_pyppeteer(self):
        pass

    def solve_captcha(self):
        pass