"""GlobalLink class

Raises:
    APIError: Exception
"""
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import urllib.request

class APIException(Exception):
    """API Exception
    """
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

class WellnoteSelenium:
    """Wellnote class"""
    def __init__(self,  username, password):
        self.username = username
        self.password = password
        self.base_url = "https://wellnote.jp/"
        self.driver = self.__create_driver()
        self.__login()

    @classmethod
    def __create_driver(cls):
        """Create driver

        Returns:
            seleniumrequests: seleniumrequests
        """
        options = Options()
        # options.add_argument('--headless') #Hide window
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(950, 800)
        driver.implicitly_wait(30)
        return driver


    def __login(self):
        """Login to Wellnote
        """
        print("Logging in to Wellnote")
        url = self.base_url + "login"
        self.driver.get(url)
        self.driver.find_element(by=By.ID, value='loginId').send_keys(self.username)
        self.driver.find_element(by=By.ID, value='password').send_keys(self.password)
        self.driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/main/form/button').click()
        wait = WebDriverWait(self.driver, 10)
        wait.until(expected_conditions.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/main/aside/div/div[1]/a[1]/div/div[1]/img')))

    def get_photo(self, album_id:int):
        url = self.base_url + f"albums/{album_id}"
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 10)
        wait.until(expected_conditions.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/main/section/div[2]/div[2]/div/div/div[1]')))


        h2 = self.driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/main/section/div[2]/div[1]/h2')
        alubum_name = h2.text

        match = re.search("\(([0-9]+)\)", alubum_name)
        max_num = int(match.group(1))

        # show 1st slide
        self.driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/main/section/div[2]/div[2]/div/div/div[1]').click()

        os.mkdir(f"./photos/{alubum_name}")

        for i in reversed(range(max_num)):
            num = str(i+1).zfill(3)
            active_slide = self.driver.find_element(by=By.CLASS_NAME, value="swiper-slide-active")
            img_element = active_slide.find_element(by=By.TAG_NAME, value="img")
            img_url = img_element.get_attribute("src")
            self.__download_file(img_url, f"./photos/{alubum_name}/{num}.jpg")
            if i > 1:
                self.driver.find_element(by=By.CLASS_NAME, value='swiper-button-next').click()

    def __download_file(self, url, dst_path):
        try:
            with urllib.request.urlopen(url) as web_file:
                data = web_file.read()
                with open(dst_path, mode='wb') as local_file:
                    local_file.write(data)
        except urllib.error.URLError as e:
            print(e)

def main():
    """main
    """

    album_ids = [
        "306636",
        "314089",
        "328728",
        "328729",
        "350494",
        "357073",
        "358498",
        "386608",
        "386878",
        "386879",
        ]

    wellclass = WellnoteSelenium(os.getenv('USER'), os.getenv('PASS'))
    for album_id in album_ids:
        wellclass.get_photo(album_id)
        print(album_id)

if __name__ == "__main__":
    main()
