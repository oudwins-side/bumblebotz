# Selenium: automation of browser
from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver.v2 as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotVisibleException
from selenium.webdriver.common.action_chains import ActionChains

# some other imports
import time
import atexit
import os
import random

# helpers
from bumblebot.helpers.geomatch_helper import Geomatch
from bumblebot.helpers.constants_helper import Printouts
from bumblebot.helpers.selectors import box_swipes_disabled_class, match_popup_class, match_popup_btn_xpath

class Session:

    HOME_URL = "https://bumble.com/app"

    def __init__(self, headless=False, store_session=True):
        self.session_data = {
            "duration": 0,
            "like": 0,
            "dislike": 0,
            "superlike": 0
        }
        self.started = False
        start_session = time.time()

        # this function will run when the session ends
        @atexit.register
        def cleanup():
            # End session duration
            seconds = int(time.time() - start_session)
            self.session_data["duration"] = seconds
            
            # add session data into a list of messages
            lines = []
            for key in self.session_data:
                message = "{}: {}".format(key, self.session_data[key])
                lines.append(message)
            
            try:
                box = self._get_msg_box(lines=lines, title="Bumblebotz")
                print(box)
            finally:
                start = None
                if not self.started:
                    start = "Failed before session start"
                else:
                    start = time.strftime("%Y-%m-%d %H:%M:%S", self.started)
                print("Started session: {}".format(start))
                
                end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print("Ended session: {}".format(end))
        
        # Go further with the initialisation
        # Setting some options of the browser here below

        options = uc.ChromeOptions()

        # Create empty profile to avoid annoying Mac Popup
        # if store_session:
        #     if not os.path.isdir(f'./chrome_profile'):
        #         os.mkdir(f'./chrome_profile')

        #     Path(f'./chrome_profile/First Run').touch()
        #     options.add_argument(f'--user-data-dir=./chrome_profile/')
        
        #options.add_argument("--user-data-dir=C:\Users\pc\AppData\Local\Google\Chrome\User Data\Default")
        options.add_argument("--user-data-dir=C:\\Users\\pc\\AppData\\Local\\Google\\Chrome\\User Data\\Default")


        options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        options.add_argument("--lang=en-GB")

        if headless:
            options.headless = True
        
         # Getting the chromedriver from cache or download it from internet
        print("Getting ChromeDriver ...")
        self.browser = uc.Chrome(options=options) #ChromeDriverManager().install(),
        #self.browser = webdriver.Chrome(options=options)
        self.browser.set_window_size(1250, 750)

        # clear the console based on the operating system you're using
        os.system('cls' if os.name == 'nt' else 'clear')

        # Cool banner
        print(Printouts.BANNER)
        time.sleep(1)

        self.started = time.localtime()
        print("Started session: {}\n\n".format(time.strftime("%Y-%m-%d %H:%M:%S", self.started)))

    # Setting a custom location
    def set_custom_location(self, latitude, longitude, accuracy="100%"):

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": int(accuracy.split('%')[0])
        }

        self.browser.execute_cdp_cmd("Page.setGeolocationOverride", params)

    def like(self, amount=1, ratio='100%', sleep=None):

        ratio = float(ratio.split('%')[0]) / 100

        if self._is_logged_in():
            helper = Geomatch(browser=self.browser)
            amount_liked = 0

            # ! Handle Unexpected issues
            # Handle Pop ups
            self._handle_pop_ups()
            # Checking if ran out of likes
            if self._is_out_of_likes():
                print("Cannot like anymore, you ran out of likes. Exiting like function")
                return
            
            # Liking profiles
            while amount_liked < amount:
                if random.random() <= ratio:
                    if helper.like():
                        amount_liked += 1
                        # update after session stats
                        self.session_data['like'] += 1
                else:
                    if helper.dislike():
                        self.session_data['dislike'] += 1
                
                # Handle Popups
                self._handle_pop_ups()
                # Checking if ran out of likes
                if self._is_out_of_likes():
                    print("Cannot like anymore, you ran out of likes. Exiting like function")
                    break

                time.sleep(random.randrange(sleep['min'], sleep['max']))
            self._print_liked_stats()



    def _is_logged_in(self):
        # make sure tinder website is loaded for the first time
        if not "bumble.com/app" in self.browser.current_url:
            # enforce english language
            self.browser.get("https://bumble.com/app")
            time.sleep(5)

        if "bumble.com/app" in self.browser.current_url:
            return True
        else:
            print("User is not logged in yet.\n")
            return False
    
    def _get_msg_box(self, lines, indent=1, width=None, title=None):
        """Print message-box with optional title."""
        space = " " * indent
        if not width:
            width = max(map(len, lines))
        box = f'/{"=" * (width + indent * 2)}\\\n'  # upper_border
        if title:
            box += f'|{space}{title:<{width}}{space}|\n'  # title
            box += f'|{space}{"-" * len(title):<{width}}{space}|\n'  # underscore
        box += ''.join([f'|{space}{line:<{width}}{space}|\n' for line in lines])
        box += f'\\{"=" * (width + indent * 2)}/'  # lower_border
        return box
    
    def _handle_pop_ups(self):
        delay = 0.25
        # Trying to handle match popup
        try: 
            WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, match_popup_class)))

            deny_button = self.browser.find_element_by_xpath(match_popup_btn_xpath)

            ActionChains(self.browser).move_to_element(deny_button).click(deny_button).perform()

        except NoSuchElementException:
            pass
        except TimeoutException:
            pass

    def _is_out_of_likes(self)->bool:
        delay = 0.25
        try:
            WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, box_swipes_disabled_class)))
            return True
        except NoSuchElementException:
            pass
        except TimeoutException:
            pass
        return False


    def _print_liked_stats(self):
        likes = self.session_data['like']
        dislikes = self.session_data['dislike']
        superlikes = self.session_data['superlike']

        if superlikes > 0:
            print(f"You've superliked {self.session_data['superlike']} profiles during this session.")
        if likes > 0:
            print(f"You've liked {self.session_data['like']} profiles during this session.")
        if dislikes > 0:
            print(f"You've disliked {self.session_data['dislike']} profiles during this session.")