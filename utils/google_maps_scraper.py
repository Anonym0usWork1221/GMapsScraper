from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchElementException,
                                        StaleElementReferenceException,
                                        NoSuchWindowException)
from selenium_stealth import stealth
from random import choice
from os.path import exists
from os import mkdir
from time import time

from utils.web_site_scraper import PatternScrapper
from utils.dict_cleaner_and_writer import DictCleaner
from utils.output_files_formats import CSVCreator
from utils.pprints import PPrints
from utils.random_users import users
from threading import Lock, Event


class GoogleMaps:
    """
    A web scraping class for extracting data from Google Maps search results.

    Attributes:
        _maps_url (str): The base URL for Google Maps.
        _finger_print_defender_ext (str): Path to the fingerprint defender browser extension.

    Methods:
        __init__(self, driver_path, unavailable_text, headless, wait_time, suggested_ext,
                 output_path, verbose, print_lock, result_range, stop_event):
            Initialize the GoogleMaps scraper instance.

        is_path_available(self):
            Check if the output directory exists and create it if not.

        create_chrome_driver(self):
            Create and configure a Chrome WebDriver instance.

        load_url(self, driver, url):
            Load a URL in the given WebDriver instance.

        search_query(self, query):
            Perform a search query on Google Maps.

        validate_result_link(self, result, driver):
            Validate and process a search result link.

        get_cover_image(self):
            Get the cover image source URL from a search result.

        get_title(self, driver):
            Get the title of a search result card.

        get_rating_in_card(self, driver):
            Get the rating of a search result card.

        get_privacy_price(self, driver):
            Get the privacy price of a search result card.

        get_category(self, driver):
            Get the category of a search result card.

        get_address(self, driver):
            Get the address of a search result card.

        get_working_hours(self, driver):
            Get the working hours of a search result card.

        get_menu_link(self, driver):
            Get the menu link of a search result card.

        get_website_link(self, driver):
            Get the website link of a search result card.

        get_phone_number(self, driver):
            Get the phone number of a search result card.

        get_related_images_list(self, driver):
            Get the related images list of a search result card.

        get_about_description(self, driver):
            Get the description of a search result card.

        reset_driver_for_next_run(self, result, driver):
            Reset the driver to its main window after processing a search result.

        scroll_to_the_end_event(self, driver):
            Scroll to the end of search results and collect them.

        _scrape_result_and_store(self, driver, mode, result, query, results_indices):
            Scrape and store data from a search result.

        start_scrapper(self, query):
            Start the scraping process for a given query.
    """

    _maps_url = "https://www.google.com/maps"
    _finger_print_defender_ext = "./extensions/finger_print_defender.crx"

    def __init__(self, driver_path: str, unavailable_text: str = "Not Available", headless: bool = False,
                 wait_time: int = 15, suggested_ext: list = None,
                 output_path: str = "./CSV_FILES", verbose: bool = True,
                 print_lock: Lock = None, result_range: int = None,
                 stop_event: Event = Event()) -> None:
        """
        Initialize the GoogleMaps scraper instance.

            :param driver_path: Path to the Chrome driver executable.
            :param unavailable_text: Placeholder text for unavailable data.
            :param headless: If True, run the browser in headless mode.
            :param wait_time: Maximum wait time for WebDriverWait.
            :param suggested_ext: List of suggested file extensions to search for on websites.
            :param output_path: Path to the directory where output files will be stored.
            :param verbose: If True, print detailed status messages.
            :param print_lock: A threading.Lock instance for synchronized printing.
            :param result_range: Limit the number of results to be scraped.
            :param stop_event: A threading.Event instance for stopping the scraping process.
        """

        if suggested_ext is None:
            suggested_ext = []

        self._unavailable_text = unavailable_text
        self._headless = headless
        self._wait_time = wait_time
        self._wait = None
        self._main_handler = None
        self._suggested_ext = suggested_ext
        self._output_path = output_path
        self._verbose = verbose
        self._results_range = result_range
        self._thread_lock = print_lock

        self._web_pattern_scraper = PatternScrapper()
        self._csv_creator = CSVCreator(file_lock=print_lock, output_path=output_path)
        self._dict_cleaner = DictCleaner(unavailable_data=unavailable_text)
        self._print = PPrints(print_lock=print_lock)
        self._driver_path = driver_path
        self._stop_event = stop_event

        # Create path if not available
        self.is_path_available()

    def is_path_available(self) -> None:
        """
        Check if the output directory exists and create it if not.
        """

        if not exists(self._output_path):
            mkdir(self._output_path)

    def create_chrome_driver(self) -> WebDriver:
        """
        Create and configure a Chrome WebDriver instance.
            :return: A configured Chrome WebDriver instance.
        """

        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-infobars')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        # options.add_argument("--disable-web-security")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-setgid-sandbox")
        options.add_argument("--no-sandbox")
        options.add_argument("--no-first-run")

        options.add_argument("--title=Developer - Abdul Moez")
        options.add_extension(self._finger_print_defender_ext)

        # Set Chrome options to prevent fingerprinting
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-features=site-per-process")
        options.add_argument("--disable-features=CrossSiteDocumentBlockingIfIsolating")
        options.add_argument("--disable-features=IsolateOrigins")
        options.add_argument("--disable-features=site-per-process")
        options.add_argument("--disable-features=AudioServiceOutOfProcess")
        options.add_argument("--disable-features=site-per-process")
        options.add_argument("--disable-features=OutOfBlinkCors")
        options.add_argument("--disable-features=OutOfBlinkCORB")
        options.add_argument("--disable-webgl")
        options.add_argument("--disable-accelerated-2d-canvas")
        options.add_argument("--disable-plugins-discovery")

        # Set the user agent to a random one to prevent fingerprinting
        options.add_argument(f"--user-agent={choice(users)}")

        # Set the window size and position to prevent fingerprinting
        options.add_argument("--window-size=1366,768")
        options.add_argument("--window-position=0,0")

        # Disable data leakage
        options.add_argument("--disable-sync")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-remote-fonts")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-component-update")
        options.add_argument("--disable-sync-preferences")

        if self._headless:
            options.add_argument("--headless=new")

        driver = Chrome(service=Service(self._driver_path), options=options)
        stealth(
            driver=driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            run_on_insecure_origins=False
        )
        self._wait = WebDriverWait(driver, self._wait_time, ignored_exceptions=(NoSuchElementException,
                                                                                StaleElementReferenceException))
        return driver

    @staticmethod
    def load_url(driver: WebDriver, url: str) -> None:
        """
        Load a URL in the given WebDriver instance.
            :param driver: The WebDriver instance.
            :param url: The URL to load.
        """

        driver.get(url)

    def search_query(self, query: str) -> None:
        """
        Perform a search query on Google Maps.
            :param query: The search query to perform.
        """
        search_box = self._wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

    def validate_result_link(self, result: any, driver: WebDriver) -> tuple[str, str, str]:
        """
        Validate and process a search result link.
            :param result: The search result link element.
            :param driver: The WebDriver instance.
            :return: A tuple containing latitude, longitude, and the link.
        """

        if result != "continue":
            get_link = result.get_attribute("href")

            driver.execute_script(f'''window.open("{get_link}", "_blank");''')
            driver.switch_to.window(driver.window_handles[-1])
        else:
            get_link = driver.current_url

        try:
            self._wait.until(EC.url_contains("@"))
            lat_lng = driver.current_url.split("@")[1].split(",")[:2]
        except Exception:
            lat_lng = [self._unavailable_text, self._unavailable_text]
            ...

        return lat_lng[0], lat_lng[1], get_link

    def get_cover_image(self) -> str:
        """
        Get the cover image source URL from a search result.
            :return: The cover image source URL.
        """
        try:
            cover_image = self._wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div['
                                                                                     '1]/div[2]/div/div['
                                                                                     '1]/div/div/div[1]/div['
                                                                                     '1]/button/img')))
            cover_image_src = cover_image.get_attribute("src")
        except Exception:
            cover_image_src = self._unavailable_text

        return cover_image_src

    def get_title(self, driver: WebDriver) -> str:
        """
        Get the title of a search result card.
            :param driver: The WebDriver instance.
            :return: The title text or the unavailable text.
        """

        try:
            title = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > '
                                                         'div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > '
                                                         'div.lMbq3e > div:nth-child(1) > h1')
            title_text = title.text
        except Exception:
            title_text = self._unavailable_text
            ...
        return title_text

    def get_rating_in_card(self, driver: WebDriver) -> str:
        """
        Get the rating of a search result card.
            :param driver: The WebDriver instance.
            :return: The rating text or the unavailable text.
        """

        try:
            rating = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div '
                                                          '> div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > '
                                                          'div.lMbq3e > div.LBgpqf > div > div.fontBodyMedium.dmRWX > '
                                                          'div.F7nice > span:nth-child(1) > span:nth-child(1)')
            rating_text = rating.text
        except Exception:
            rating_text = self._unavailable_text
            ...
        return rating_text

    def get_privacy_price(self, driver: WebDriver) -> str:
        """
        Get the privacy of a search result card.
            :param driver: The WebDriver instance.
            :return: The privacy text or the unavailable text.
        """

        try:
            price_privacy = driver.find_element(By.XPATH,
                                                '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div['
                                                '2]/div/div[1]/div[2]/div/div[1]/span/span/span/span[2]/span/span'
                                                )

            price_privacy_text = price_privacy.text
        except Exception:
            price_privacy_text = self._unavailable_text
            ...
        return price_privacy_text

    def get_category(self, driver: WebDriver) -> str:
        """
        Get the category of a search result card.
            :param driver: The WebDriver instance.
            :return: The category text or the unavailable text.
        """

        try:
            category = driver.find_element(By.CSS_SELECTOR,
                                           '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > '
                                           'div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > div.lMbq3e '
                                           '> '
                                           'div.LBgpqf > div > div:nth-child(2) > span > span > button')
            category_text = category.text

        except Exception:
            category_text = self._unavailable_text
            ...
        return category_text

    def get_address(self, driver: WebDriver) -> str:
        """
        Get the address of a search result card.
            :param driver: The WebDriver instance.
            :return: The address text or the unavailable text.
        """

        try:
            address = driver.find_element(By.CLASS_NAME, 'rogA2c')
            address_text = address.text
        except Exception:
            address_text = self._unavailable_text
            ...
        return address_text

    def get_working_hours(self, driver: WebDriver) -> str:
        """
        Get the hours of a search result card.
            :param driver: The WebDriver instance.
            :return: The hours text or the unavailable text.
        """

        try:
            driver.find_element(By.CSS_SELECTOR, 'div.OqCZI.fontBodyMedium.WVXvdc > div.OMl5r.hH0dDd.jBYmhd').click()

            working_hours = driver.find_element(By.CSS_SELECTOR, 'div.t39EBf.GUrTXd > div > table')
            working_hours_text = working_hours.text.strip().split("\n")
            working_hours_text = [x.strip() for x in working_hours_text if x]
            working_hours_text = ",".join(working_hours_text)
        except Exception:
            working_hours_text = self._unavailable_text
            ...
        return working_hours_text

    def get_menu_link(self, driver: WebDriver) -> str:
        """
        Get the menu_link of a search result card.
            :param driver: The WebDriver instance.
            :return: The menu_link text or the unavailable text.
        """

        try:
            menu_link = driver.find_element(By.CSS_SELECTOR,
                                            'div.UCw5gc > div > div:nth-child(1) > a[data-tooltip="Open menu link"]')
            menu_link_href = menu_link.get_attribute("href")

        except Exception as e:
            menu_link_href = self._unavailable_text
            ...
        return menu_link_href

    def get_website_link(self, driver: WebDriver) -> str:
        """
        Get the web_link of a search result card.
            :param driver: The WebDriver instance.
            :return: The web_link text or the unavailable text.
        """

        try:
            website = driver.find_element(By.CSS_SELECTOR, 'div.UCw5gc > div > div:nth-child(1) > a['
                                                           'data-tooltip="Open website"]')
            website_href = website.get_attribute("href")

        except Exception as e:
            website_href = self._unavailable_text
            ...
        return website_href

    def get_phone_number(self, driver: WebDriver) -> str:
        """
        Get the phone number of a search result card.
            :param driver: The WebDriver instance.
            :return: The phone number text or the unavailable text.
        """

        try:
            phone = driver.find_elements(By.CLASS_NAME, 'rogA2c')
            try:
                for ph in phone:
                    ph_text = ph.text.replace("(", "").replace(")", "").replace(" ", "").replace("+", "").replace("-",
                                                                                                                  "")
                    if ph_text.isnumeric():
                        phone = ph

                phone_href = phone.text
            except Exception:
                phone_href = self._unavailable_text

        except Exception as e:
            phone_href = self._unavailable_text
            ...
        return phone_href

    def get_related_images_list(self, driver: WebDriver) -> str:
        """
        Get the images of a search result card.
            :param driver: The WebDriver instance.
            :return: The images text or the unavailable text.
        """

        try:
            related_images = driver.find_elements(By.CLASS_NAME, "DaSXdd")
            if related_images:
                related_images_src = [image.get_attribute("src") for image in related_images]
                related_images_data = ",".join(related_images_src)
            else:
                related_images_data = self._unavailable_text

        except Exception as e:
            related_images_data = self._unavailable_text
            ...
        return related_images_data

    def get_about_description(self, driver: WebDriver) -> dict:
        """
        Get the description of a search result card.
            :param driver: The WebDriver instance.
            :return: The description text or the unavailable text dict.
        """

        try:
            driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > '
                                                 'div.e07Vkf.kA9KIf > div > div > div:nth-child(3) > div > div > '
                                                 'button:nth-child(3)').click()

            self._wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#QA0Szd > div > div > '
                                                                              'div.w6VYqd > div.bJzME.tTVLSc '
                                                                              '> div > div.e07Vkf.kA9KIf > '
                                                                              'div > div > '
                                                                              'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')))

            # about_data = driver.find_elements(By.CSS_SELECTOR, 'div.iP2t7d.fontBodyMedium')
            about_dict = {}
            try:
                about_text = driver.find_element(By.CSS_SELECTOR,
                                                 '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > '
                                                 'div > div.e07Vkf.kA9KIf > div > div > '
                                                 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.PbZDve > p > '
                                                 'span > span')
                about_dict["about_desc"] = about_text.text
            except NoSuchElementException:
                about_dict["about_desc"] = self._unavailable_text
                ...

            # for data_dic in about_data:
            #     title = data_dic.find_element(By.CSS_SELECTOR, "h2").text
            #     desc = data_dic.text.replace(title.strip(), "").split("\n")
            #     desc = [x.strip() for x in desc if x]
            #     desc_data = ",".join(desc)
            #     about_dict[title.strip()] = desc_data

        except Exception as e:
            about_dict = {"about_desc": self._unavailable_text}
            ...
        return about_dict

    def reset_driver_for_next_run(self, result: any, driver: WebDriver) -> None:
        """
        Reset the driver to its main window after processing a search result.
            :param result: The search result link element.
            :param driver: The WebDriver instance.
        """
        if result != "continue":
            driver.close()
            driver.switch_to.window(self._main_handler)
            self._wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc")))

    def scroll_to_the_end_event(self, driver: WebDriver) -> list:
        """
        Scroll to the end of search results and collect them.
            :param driver: The WebDriver instance.
            :return: A list of collected search result elements.
        """

        try:
            self._wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc")))
        except TimeoutException:
            results = ["continue"]
            return results

        scroll_end = 'div.PbZDve  > p.fontBodyMedium  > span > span[class="HlvSq"]'
        start_time = time()
        scroll_wait = 1
        while True:
            results = driver.find_elements(By.CLASS_NAME, 'hfpxzc')
            if self._results_range:
                if len(results) >= self._results_range:
                    temp_results = results[:self._results_range + 1]
                    results = temp_results
                    break

            driver.execute_script('arguments[0].scrollIntoView(true);', results[-1])
            driver.implicitly_wait(scroll_wait)
            try:
                text_span = driver.find_element(By.CSS_SELECTOR, scroll_end)
                if "you've reached the end" in text_span.text.lower():
                    break
            except NoSuchElementException:
                ...

            elapsed_time = time() - start_time
            if elapsed_time > (30 << 1):  # 60 seconds = 1 minutes
                break

        return results

    def _scrape_result_and_store(self, driver: WebDriver, mode: str, result: any, query: str,
                                 results_indices: list[int, int]):
        """
        Scrape and store data from a search result.
            :param driver: The WebDriver instance.
            :param mode: The mode of the scraper (headless or windowed).
            :param result: The search result link element.
            :param query: The search query.
            :param results_indices: A list containing the current and total indices of results being processed.
        """

        temp_data = {}

        # latitude and longitude
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting Latitude and longitude", mode=mode,
                                        results_indices=results_indices)
        lat, long, map_link = self.validate_result_link(result, driver)

        # get cover image
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting cover image", mode=mode,
                                        results_indices=results_indices)
        cover_image = self.get_cover_image()

        # get title
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting title", mode=mode,
                                        results_indices=results_indices)
        card_title = self.get_title(driver)

        # get rating
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting rating", mode=mode,
                                        results_indices=results_indices)
        card_rating = self.get_rating_in_card(driver)

        # Get privacy price
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting privacy price", mode=mode,
                                        results_indices=results_indices)
        privacy_price = self.get_privacy_price(driver)

        # get category
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting Category", mode=mode,
                                        results_indices=results_indices)
        card_category = self.get_category(driver)

        # get address
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting Address", mode=mode,
                                        results_indices=results_indices)
        card_address = self.get_address(driver)

        # get working hours
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting Working hours", mode=mode,
                                        results_indices=results_indices)
        card_hours = self.get_working_hours(driver)

        # get menu link
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting Menu Links", mode=mode,
                                        results_indices=results_indices)
        card_menu_link = self.get_menu_link(driver)

        # get website link
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting WebLink", mode=mode,
                                        results_indices=results_indices)
        card_website_link = self.get_website_link(driver)

        # get website data
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting WebLink Data", mode=mode,
                                        results_indices=results_indices)
        website_data = self._web_pattern_scraper.find_patterns(driver, card_website_link, self._suggested_ext,
                                                               self._unavailable_text)

        # get phone number
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting Phone Number", mode=mode,
                                        results_indices=results_indices)
        card_phone_number = self.get_phone_number(driver)

        # get card images
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting Images links", mode=mode,
                                        results_indices=results_indices)
        card_related_images = self.get_related_images_list(driver)

        # get card about
        if self._verbose:
            self._print.print_with_lock(query=query, status="Getting About data", mode=mode,
                                        results_indices=results_indices)
        card_about = self.get_about_description(driver)

        # Reset driver again
        if self._verbose:
            self._print.print_with_lock(query=query, status="Resetting Driver", mode=mode,
                                        results_indices=results_indices)
        self.reset_driver_for_next_run(result, driver)

        # Store scrapped data
        if self._verbose:
            self._print.print_with_lock(query=query, status="Storing Data in List", mode=mode,
                                        results_indices=results_indices)

        temp_data["title"] = card_title
        temp_data["map_link"] = map_link
        temp_data["cover_image"] = cover_image
        temp_data["rating"] = card_rating
        temp_data["privacy_price"] = privacy_price
        temp_data["category"] = card_category
        temp_data["address"] = card_address
        temp_data["working_hours"] = card_hours
        temp_data["menu_link"] = card_menu_link
        temp_data["webpage"] = card_website_link
        temp_data["phone_number"] = card_phone_number
        temp_data["related_images"] = card_related_images
        temp_data["latitude"] = lat
        temp_data["longitude"] = long

        # pattern evaluation of website
        temp_data.update(website_data)

        # store about related data
        temp_data.update(card_about)

        # Store data in runtime
        temp_list = [temp_data]
        if self._verbose:
            self._print.print_with_lock(query=query, status="Dumping data in CSV file", mode=mode)
        self._csv_creator.create_csv(list_of_dict_data=temp_list)

    def start_scrapper(self, query: str) -> None:
        """
        Start the scraping process for a given query.
            :param query: The search query.
        """

        if self._headless:
            mode = "headless"
        else:
            mode = "windowed"

        try:
            if self._verbose:
                self._print.print_with_lock(query=query, status="Initializing Browser", mode=mode)
            else:
                self._print.print_with_lock(query=query, status="Running the script", mode=mode)

            driver = self.create_chrome_driver()

            if self._verbose:
                self._print.print_with_lock(query=query, status="Loading URL", mode=mode)

            if "http" in query.lower().strip():
                self.load_url(driver, query)
            else:
                self.load_url(driver, self._maps_url)

            if self._verbose:
                self._print.print_with_lock(query=query, status="Searching query", mode=mode)

            if "http" not in query:
                self.search_query(query)
            self._main_handler = driver.current_window_handle

            if self._verbose:
                self._print.print_with_lock(query=query, status="Loading Links from GMAPS", mode=mode)

            # load all the results
            results = self.scroll_to_the_end_event(driver)

            result_indices = [len(results), 1]
            for result in results:
                if self._stop_event.is_set():
                    break
                # Scrape and store data
                self._scrape_result_and_store(driver=driver, mode=mode, result=result, query=query,
                                              results_indices=result_indices)
                result_indices[1] += 1

            if self._verbose:
                self._print.print_with_lock(query=query, status="Driver Closed", mode=mode)
            driver.close()
            # Clean the data
            # if self._verbose:
            #     self._print.print_with_lock(query=query, status="Cleaning Collected Data", mode=mode)
            # scrapped_data_list = self._dict_cleaner.start_cleaning_dict_data(scrapped_data_list)

            # Create a csv file
            # if self._verbose:
            #     self._print.print_with_lock(query=query, status="Dumping data in CSV file", mode=mode)
            # self._csv_creator.create_csv(list_of_dict_data=scrapped_data_list, query=query)
        except NoSuchWindowException:
            if self._verbose:
                self._print.print_with_lock(query=query, status="Browser Closed", mode=mode)

# if __name__ == '__main__':
#     App = GoogleMaps()
#     # App.start_scrapper("Girl & The Goat")
#     App.start_scrapper("restaurants near me")
