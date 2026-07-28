from selenium.common.exceptions import (TimeoutException, NoSuchElementException, StaleElementReferenceException,
                                        NoSuchWindowException)
from utils.output_files_formats import CSVCreator, XLSXCreator, JSONCreator
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from utils.web_site_scraper import PatternScrapper
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from utils.pprints import PPrints
from threading import Lock, Event
from subprocess import check_output, DEVNULL
from platform import system as platform_system
from time import time, sleep
from random import uniform
from os import makedirs
import re


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

    # hl=en forces the English UI so the aria-label/text-based selectors used below
    # (hours, about, cover photo, price) resolve regardless of the visitor's region.
    _maps_url = "https://www.google.com/maps?hl=en"
    _finger_print_defender_ext = "./extensions/finger_print_defender.crx"

    def __init__(self, unavailable_text: str = "Not Available", output_format: str = "CSV",
                 headless: bool = False,
                 wait_time: int = 15, suggested_ext: list = None,
                 output_path: str = "./OUTPUT_FILES", verbose: bool = True,
                 print_lock: Lock = None, result_range: int = None,
                 stop_event: Event = Event(),
                 scroll_minutes: int = 1,
                 gl: str = None
                 ) -> None:
        """
        Initialize the GoogleMaps scraper instance.
            :param unavailable_text: Placeholder text for unavailable data.
            :param output_format: Format for storing output data.
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
        print_lock = print_lock or Lock()
        self._thread_lock = print_lock
        self.__output_format = output_format
        self._scroll_minutes = scroll_minutes
        self._maps_url = "https://www.google.com/maps?hl=en"
        if gl:
            self._maps_url += f"&gl={gl}"


        self._web_pattern_scraper = PatternScrapper()
        if self.__output_format.lower() == "json":
            self._file_creator = JSONCreator(file_lock=print_lock, output_path=output_path)
        elif self.__output_format.lower() == "excel":
            self._file_creator = XLSXCreator(file_lock=print_lock, output_path=output_path)
        else:
            self._file_creator = CSVCreator(file_lock=print_lock, output_path=output_path)
        self._print = PPrints(print_lock=print_lock)
        self._stop_event = stop_event
        self.__mode = "headless" if self._headless else "windowed"

        # Create a path if not available
        self.is_path_available()

    def is_path_available(self) -> None:
        """
        Check if the output directory exists and create it if not.
        """

        # exist_ok prevents a race when multiple worker threads create the
        # output directory at the same time (it raised FileExistsError before).
        makedirs(self._output_path, exist_ok=True)

    @staticmethod
    def detect_chrome_major_version() -> int:
        """
        Detect the installed Chrome/Chromium major version so undetected-chromedriver
        downloads a matching driver instead of the latest one. Without this, uc defaults
        to the newest driver and fails with "This version of ChromeDriver only supports
        Chrome version N" when the installed browser is older.
            :return: The Chrome major version, or 0 (uc's auto/latest) if it can't be found.
        """

        try:
            chrome_path = uc.find_chrome_executable()
            if not chrome_path:
                return 0
            if platform_system().lower() == "windows":
                # chrome.exe does not print --version to stdout on Windows.
                command = ["powershell", "-NoProfile", "-Command",
                           f"(Get-Item '{chrome_path}').VersionInfo.ProductVersion"]
            else:
                command = [chrome_path, "--version"]
            output = check_output(command, stderr=DEVNULL).decode("utf-8", "ignore")
            match = re.search(r"(\d+)\.", output)
            return int(match.group(1)) if match else 0
        except Exception as e:
            _ = e
            return 0

    def create_chrome_driver(self) -> WebDriver:
        """
        Create and configure a Chrome WebDriver instance.
            :return: A configured Chrome WebDriver instance.
        """

        options = uc.ChromeOptions()
        options.add_argument(argument='--title=Developer - Abdul Moez')
        options.add_argument(argument='--disable-popup-blocking')
        options.add_extension(extension=self._finger_print_defender_ext)
        chrome_version = self.detect_chrome_major_version()
        driver = uc.Chrome(options=options, headless=self._headless, use_subprocess=False,
                           version_main=chrome_version or None)
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
        # Google Maps replaced id="searchboxinput" with a combobox <input name="q">
        # that has a dynamic id. Accept both so old and new layouts work.
        search_box = self._wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input#searchboxinput, input[name='q'], input[role='combobox']")))
        search_box.click()
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
            # Pass the href as an argument so a URL containing quotes can't break the script.
            driver.execute_script('window.open(arguments[0], "_blank");', get_link)
            driver.switch_to.window(driver.window_handles[-1])
        else:
            get_link = None

        try:
            self._wait.until(EC.url_contains("@"))
            lat_lng = driver.current_url.split("@")[1].split(",")[:2]
        except Exception as e:
            _ = e
            lat_lng = [self._unavailable_text, self._unavailable_text]

        # Single-place ('continue') flow: capture the canonical URL only after the
        # redirect to the place page has settled.
        if get_link is None:
            get_link = driver.current_url

        return lat_lng[0], lat_lng[1], get_link

    def get_cover_image(self, driver: WebDriver) -> str:
        """
        Get the cover image source URL from a search result.
            :param driver: The WebDriver instance.
            :return: The cover image source URL.
        """
        try:
            # Wait for the place panel to settle: Maps often renders an empty <h1>
            # first, so wait for non-empty title text. This also makes the panel
            # ready for every extractor that follows.
            self._wait.until(lambda drv: (drv.find_element(By.CSS_SELECTOR, "h1").text or "").strip())
            images = driver.find_elements(By.CSS_SELECTOR, "button[aria-label^='Photo'] img")
            if not images:
                images = [img for img in driver.find_elements(By.CSS_SELECTOR, "img")
                          if "googleusercontent" in (img.get_attribute("src") or "")]
            cover_image_src = (images[0].get_attribute("src") if images else "") or self._unavailable_text
        except Exception as e:
            _ = e
            cover_image_src = self._unavailable_text
        return cover_image_src

    def get_title(self, driver: WebDriver) -> str:
        """
        Get the title of a search result card.
            :param driver: The WebDriver instance.
            :return: The title text or the unavailable text.
        """

        try:
            # Wait for non-empty title text (the panel can render an empty <h1> first).
            title_text = self._wait.until(
                lambda drv: (drv.find_element(By.CSS_SELECTOR, "h1").text or "").strip()) or self._unavailable_text
        except Exception as e:
            _ = e
            title_text = self._unavailable_text
        return title_text

    def get_rating_in_card(self, driver: WebDriver) -> str:
        """
        Get the rating of a search result card.
            :param driver: The WebDriver instance.
            :return: The rating text or the unavailable text.
        """

        try:
            rating = driver.find_element(By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']")
            rating_text = rating.text or self._unavailable_text
        except Exception as e:
            _ = e
            rating_text = self._unavailable_text
        return rating_text

    def get_privacy_price(self, driver: WebDriver) -> str:
        """
        Get the privacy of a search result card.
            :param driver: The WebDriver instance.
            :return: The privacy text or the unavailable text.
        """

        try:
            price_privacy_text = self._unavailable_text
            for element in driver.find_elements(By.CSS_SELECTOR, "span[aria-label]"):
                aria = element.get_attribute("aria-label") or ""
                if aria.startswith("Price"):
                    price_privacy_text = (element.text.strip()
                                          or aria.replace("Price:", "").strip()
                                          or self._unavailable_text)
                    break
        except Exception as e:
            _ = e
            price_privacy_text = self._unavailable_text
        return price_privacy_text

    def get_category(self, driver: WebDriver) -> str:
        """
        Get the category of a search result card.
            :param driver: The WebDriver instance.
            :return: The category text or the unavailable text.
        """

        try:
            category_text = driver.find_element(By.CSS_SELECTOR, "button.DkEaL").text or self._unavailable_text
        except Exception as e:
            _ = e
            category_text = self._unavailable_text
        return category_text

    def get_address(self, driver: WebDriver) -> str:
        """
        Get the address of a search result card.
            :param driver: The WebDriver instance.
            :return: The address text or the unavailable text.
        """

        try:
            address = driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']")
            value = address.find_elements(By.CSS_SELECTOR, ".Io6YTe")
            if value and value[0].text.strip():
                address_text = value[0].text.strip()
            else:
                address_text = (address.get_attribute("aria-label") or "").replace("Address:", "").strip() \
                               or self._unavailable_text
        except Exception as e:
            _ = e
            address_text = self._unavailable_text
        return address_text

    def get_working_hours(self, driver: WebDriver) -> str:
        """
        Get the hours of a search result card.
            :param driver: The WebDriver instance.
            :return: The hours text or the unavailable text.
        """

        try:
            # Expand the weekly view when the toggle is present (reliable in
            # windowed mode; headless typically exposes only the current day).
            toggles = driver.find_elements(
                By.CSS_SELECTOR, "[aria-label='Show open hours for the week'], [data-item-id='oh']")
            if toggles:
                try:
                    toggles[0].click()
                except Exception:
                    try:
                        driver.execute_script("arguments[0].click();", toggles[0])
                    except Exception:
                        pass
                sleep(uniform(0.4, 0.8))

            day_order = {day: i for i, day in enumerate(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])}
            rows = {}
            for element in driver.find_elements(By.CSS_SELECTOR, "[aria-label]"):
                aria = (element.get_attribute("aria-label") or "").strip()
                match = re.match(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),", aria)
                if match:
                    clean = re.sub(r",?\s*(Copy open hours|Hide open hours|Suggest.*)$", "", aria).strip()
                    rows.setdefault(match.group(1), clean)

            if rows:
                working_hours_text = ",".join(rows[day] for day in sorted(rows, key=lambda d: day_order[d]))
            else:
                # Fallback to the current-day hours block.
                working_hours_text = self._unavailable_text
                for selector in ("div.t39EBf", "div.OqCZI"):
                    block = driver.find_elements(By.CSS_SELECTOR, selector)
                    if block and block[0].text.strip():
                        working_hours_text = re.sub(r"\s*Suggest new hours\s*$", "",
                                                    block[0].text.replace("\n", " ").strip())
                        break
        except Exception as e:
            _ = e
            working_hours_text = self._unavailable_text
        return working_hours_text

    def get_menu_link(self, driver: WebDriver) -> str:
        """
        Get the menu_link of a search result card.
            :param driver: The WebDriver instance.
            :return: The menu_link text or the unavailable text.
        """

        try:
            menu_link = driver.find_element(By.CSS_SELECTOR, "a[data-item-id='menu']")
            menu_link_href = menu_link.get_attribute("href") or self._unavailable_text

        except Exception as e:
            _ = e
            menu_link_href = self._unavailable_text
        return menu_link_href

    def get_website_link(self, driver: WebDriver) -> str:
        """
        Get the web_link of a search result card.
            :param driver: The WebDriver instance.
            :return: The web_link text or the unavailable text.
        """

        try:
            website = driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
            website_href = website.get_attribute("href") or self._unavailable_text

        except Exception as e:
            _ = e
            website_href = self._unavailable_text
        return website_href

    def get_phone_number(self, driver: WebDriver) -> str:
        """
        Get the phone number of a search result card.
            :param driver: The WebDriver instance.
            :return: The phone number text or the unavailable text.
        """

        try:
            phone = driver.find_element(By.CSS_SELECTOR, "button[data-item-id^='phone']")
            value = phone.find_elements(By.CSS_SELECTOR, ".Io6YTe")
            if value and value[0].text.strip():
                phone_href = value[0].text.strip()
            else:
                # data-item-id is "phone:tel:+49..." — fall back to that number.
                data_item_id = phone.get_attribute("data-item-id") or ""
                phone_href = data_item_id.split("tel:")[-1] if "tel:" in data_item_id else self._unavailable_text
        except Exception as e:
            _ = e
            phone_href = self._unavailable_text
        return phone_href

    def get_related_images_list(self, driver: WebDriver) -> str:
        """
        Get the images of a search result card.
            :param driver: The WebDriver instance.
            :return: The images text or the unavailable text.
        """

        try:
            related_images_src = []
            for image in driver.find_elements(By.CSS_SELECTOR, "img"):
                src = image.get_attribute("src") or ""
                if ("googleusercontent" in src or "streetviewpixels" in src) and src not in related_images_src:
                    related_images_src.append(src)
            related_images_data = ",".join(related_images_src) if related_images_src else self._unavailable_text

        except Exception as e:
            _ = e
            related_images_data = self._unavailable_text
        return related_images_data

    def get_about_description(self, driver: WebDriver) -> dict:
        """
        Get the description of a search result card.
            :param driver: The WebDriver instance.
            :return: The description text or the unavailable text dict.
        """

        about_dict = {"about_desc": self._unavailable_text}
        try:
            # "About" is now a tab in the place panel. Click it, then read the
            # "About <name>" region (amenities / description).
            for tab in driver.find_elements(By.CSS_SELECTOR, "button[role='tab']"):
                if (tab.get_attribute("aria-label") or "").startswith("About"):
                    try:
                        tab.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", tab)
                    break
            sleep(uniform(0.4, 0.8))

            regions = [region for region in driver.find_elements(By.CSS_SELECTOR, "div[aria-label^='About']")
                       if region.text.strip()]
            if regions:
                about_dict["about_desc"] = regions[0].text.strip().replace("\n", ",")
        except Exception as e:
            _ = e
            about_dict = {"about_desc": self._unavailable_text}
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

        start_time = time()
        scroll_wait = 1
        last_count = 0
        stagnant_rounds = 0
        while True:
            results = driver.find_elements(By.CLASS_NAME, 'hfpxzc')
            if self._results_range and len(results) >= self._results_range:
                results = results[:self._results_range]
                break

            # The feed can transiently return no cards while re-rendering.
            if not results:
                stagnant_rounds += 1
                if stagnant_rounds >= 5:
                    break
                sleep(uniform(0.2, 0.6))
                continue

            driver.execute_script('arguments[0].scrollIntoView(true);', results[-1])
            driver.implicitly_wait(scroll_wait)

            # Google's end-of-list marker, when present.
            end_marker = driver.find_elements(By.CSS_SELECTOR, "span.HlvSq")
            if end_marker and "reached the end" in (end_marker[-1].text or "").lower():
                break

            # Layout-independent stop: the feed stopped producing new results.
            if len(results) == last_count:
                stagnant_rounds += 1
                if stagnant_rounds >= 5:
                    break
            else:
                stagnant_rounds = 0
                last_count = len(results)

            sleep(uniform(0.2, 0.6))
            elapsed_time = time() - start_time
            if elapsed_time > (int(self._scroll_minutes) * 60):  # 60 seconds = 1 minutes
                break

        return results

    def __pprint_override(self, query: str, status: str, results_indices: any([str, list[int]]) = "Calculating"):
        if self._verbose:
            self._print.print_with_lock(
                query=query, status=status, mode=self.__mode, results_indices=results_indices
            )
        else:
            self._print.print_with_lock(
                query=query, status=f"[Verbose is off] {status}",
                mode=self.__mode, results_indices=results_indices
            )

    def _scrape_result_and_store(self, driver: WebDriver, result: any, query: str,
                                 results_indices: list[int]):
        """
        Scrape and store data from a search result.
            :param driver: The WebDriver instance.
            :param result: The search result link element.
            :param query: The search query.
            :param results_indices: A list containing the current and total indices of results being processed.
        """

        temp_data = {}

        # latitude and longitude
        self.__pprint_override(query=query, status="Getting Latitude and longitude", results_indices=results_indices)
        lat, long, map_link = self.validate_result_link(result, driver)

        # get cover image
        self.__pprint_override(query=query, status="Getting cover image", results_indices=results_indices)
        cover_image = self.get_cover_image(driver)

        # get title
        self.__pprint_override(query=query, status="Getting title", results_indices=results_indices)
        card_title = self.get_title(driver)

        # get rating
        self.__pprint_override(query=query, status="Getting rating", results_indices=results_indices)
        card_rating = self.get_rating_in_card(driver)

        # Get privacy price
        self.__pprint_override(query=query, status="Getting privacy price", results_indices=results_indices)
        privacy_price = self.get_privacy_price(driver)

        # get category
        self.__pprint_override(query=query, status="Getting Category", results_indices=results_indices)
        card_category = self.get_category(driver)

        # get address
        self.__pprint_override(query=query, status="Getting Address", results_indices=results_indices)
        card_address = self.get_address(driver)

        # get working hours
        self.__pprint_override(query=query, status="Getting Working hours", results_indices=results_indices)
        card_hours = self.get_working_hours(driver)

        # get menu link
        self.__pprint_override(query=query, status="Getting Menu Links", results_indices=results_indices)
        card_menu_link = self.get_menu_link(driver)

        # get website link
        self.__pprint_override(query=query, status="Getting WebLink", results_indices=results_indices)
        card_website_link = self.get_website_link(driver)

        # get website data
        self.__pprint_override(query=query, status="Getting WebLink Data", results_indices=results_indices)
        website_data = self._web_pattern_scraper.find_patterns(driver, card_website_link, self._suggested_ext,
                                                               self._unavailable_text)

        # get phone number
        self.__pprint_override(query=query, status="Getting Phone Number", results_indices=results_indices)
        card_phone_number = self.get_phone_number(driver)

        # get card images
        self.__pprint_override(query=query, status="Getting Images links", results_indices=results_indices)
        card_related_images = self.get_related_images_list(driver)

        # get card about
        self.__pprint_override(query=query, status="Getting About data", results_indices=results_indices)
        card_about = self.get_about_description(driver)

        # Reset driver again
        self.__pprint_override(query=query, status="Resetting Driver", results_indices=results_indices)
        self.reset_driver_for_next_run(result, driver)

        # Store scrapped data
        self.__pprint_override(query=query, status="Storing Data in List", results_indices=results_indices)

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
        self.__pprint_override(query=query, status="Dumping data in CSV file", results_indices=results_indices)
        self._file_creator.create(list_of_dict_data=temp_list)

    def start_scrapper(self, query: str) -> None:
        """
        Start the scraping process for a given query.
            :param query: The search query.
        """

        try:
            if self._verbose:
                self.__pprint_override(query=query, status="Initializing Browser")
            else:
                self.__pprint_override(query=query, status="Running the script")

            driver = self.create_chrome_driver()
            self.__pprint_override(query=query, status="Loading URL")

            if query.lower().strip().startswith("http"):
                self.load_url(driver, query)
            else:
                self.load_url(driver, self._maps_url)

            self.__pprint_override(query=query, status="Searching query")

            if not query.lower().strip().startswith("http"):
                self.search_query(query)
            self._main_handler = driver.current_window_handle

            self.__pprint_override(query=query, status="Loading Links from GMAPS")

            # load all the results
            results = self.scroll_to_the_end_event(driver)

            result_indices = [len(results), 1]
            for result in results:
                if self._stop_event.is_set():
                    break
                try:
                    # Scrape and store data
                    self._scrape_result_and_store(driver=driver, result=result, query=query,
                                                  results_indices=result_indices)
                except Exception as e:
                    # One bad result (stale element, timeout, IO error) must not abort
                    # the whole query — log it, recover the window state, and continue.
                    self.__pprint_override(query=query, status=f"Skipping result ({type(e).__name__})",
                                           results_indices=result_indices)
                    try:
                        for handle in list(driver.window_handles):
                            if handle != self._main_handler:
                                driver.switch_to.window(handle)
                                driver.close()
                        driver.switch_to.window(self._main_handler)
                    except Exception:
                        pass
                finally:
                    result_indices[1] += 1

            self.__pprint_override(query=query, status="Driver Closed")
            driver.close()
        except NoSuchWindowException:
            self.__pprint_override(query=query, status="Browser Closed")
        except Exception as e:
            # Distinguish a genuine mid-run failure from a user-closed browser.
            self.__pprint_override(query=query, status=f"Aborted ({type(e).__name__}: {e})")

if __name__ == '__main__':
    App = GoogleMaps()
    App.start_scrapper("Girl & The Goat")
    # App.start_scrapper("restaurants near me")
