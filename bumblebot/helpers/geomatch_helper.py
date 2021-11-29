from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
import time

from bumblebot.helpers.selectors import *


class Geomatch:

    DELAY = 5

    HOME_URL = "https://bumble.com/app"


    def __init__(self, browser):
        self.browser = browser
        if self.HOME_URL not in self.browser.current_url:
            self._get_home_page()
    
    def like(self)->bool:
        try:
            # wait for element to appear
            WebDriverWait(self.browser, self.DELAY).until(EC.presence_of_element_located((By.CLASS_NAME, like_button_class)))

            button = self.browser.find_elements_by_class_name(like_button_class)[0]

            ActionChains(self.browser).move_to_element(button).click(button).perform()
            
            time.sleep(1)
            return True
        
        except (TimeoutException, ElementClickInterceptedException):
            self._get_home_page()
        
        return False
    
    def dislike(self)->bool:
        try:
            # wait for element to appear
            WebDriverWait(self.browser, self.DELAY).until(EC.presence_of_element_located((By.CLASS_NAME, dislike_button_class)))

            button = self.browser.find_elements_by_class_name(dislike_button_class)[0]

            ActionChains(self.browser).move_to_element(button).click(button).perform()
            
            time.sleep(1)
            return True
        
        except (TimeoutException, ElementClickInterceptedException):
            self._get_home_page()
        
        return False


    def _get_home_page(self):
        self.browser.get(self.HOME_URL)
        time.sleep(self.DELAY)