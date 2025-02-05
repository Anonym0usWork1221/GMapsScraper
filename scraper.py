from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchElementException,
                                        StaleElementReferenceException,
                                        NoSuchWindowException)
from utils.web_site_scraper import PatternScrapper
from utils.output_files_formats import CSVCreator
import undetected_chromedriver as uc
from utils.pprints import PPrints
from threading import Lock, Event
from os.path import exists
from time import time, sleep
from os import mkdir

ext = "./extensions/finger_print_defender.crx"
maps_url = "https://www.google.com/maps"
query = "lead generation"

options = uc.ChromeOptions()
options.add_argument(argument='--title=Developer - Abdul Moez')
options.add_argument(argument='--disable-popup-blocking')
options.add_extension(extension=ext)
driver = uc.Chrome(options=options, headless=False, use_subprocess=False)
wait = WebDriverWait(driver, 15, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException))
driver.get(maps_url)

# search
search_box = wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
search_box.send_keys(query)
search_box.send_keys(Keys.RETURN)

main_handler = driver.current_window_handle
item_handler = None
first_loading = True
iterated_links = set()

while True:
    current_results = driver.find_elements(
        by=By.CSS_SELECTOR, value='div[role="feed"][aria-label^="Results"]  a[class="hfpxzc"]'
    )
    result_links = set(
        result.get_attribute(name='href') for result in current_results if
        result.get_attribute(name='href') not in iterated_links
    )
    iterated_links.update(result_links)
    driver.execute_script('arguments[0].scrollIntoView(true);', current_results[-1])
    for link in result_links:
        if first_loading:
            driver.execute_script(f'''window.open("{link}", "_blank");''')
            first_loading = False
            item_handler = driver.window_handles[-1]
            driver.switch_to.window(item_handler)
        else:
            driver.switch_to.window(item_handler)
            driver.get(link)
        # wait until latitude and longitude appears in url
        wait.until(EC.url_contains("@"))
        lat, lng = driver.current_url.split("@")[1].split(",")[:2]
        title = driver.find_element(By.CSS_SELECTOR, 'div[class="lMbq3e"] h1').text.strip()
        number_of_reviews = driver.find_element(
            By.CSS_SELECTOR, 'div[class^="F7nice"] > span + span'
        ).text.removeprefix("(").removesuffix(")").replace(',', '').strip()
        item_rating = driver.find_element(By.CSS_SELECTOR, 'div[class^="F7nice"] > span').text.strip()
        cover_image = driver.find_element(By.CSS_SELECTOR, 'button[aria-label^="Photo"] > img').get_attribute('src')
        try:
            privacy_price = driver.find_element(By.CSS_SELECTOR, 'span[aria-label^="Price"]').text.strip()
        except NoSuchElementException:
            privacy_price = ""
        category = driver.find_element(By.CSS_SELECTOR, 'button[class^="DkEaL"]').text.strip()
        address_element = driver.find_element(By.CLASS_NAME, 'rogA2c')
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});"
            , address_element)
        address = address_element.text
        menu_webpage_link = driver.find_element(
            By.CSS_SELECTOR, 'a[data-tooltip="Open menu link"]').get_attribute('href')
        webpage_link = driver.find_element(By.CSS_SELECTOR, 'a[data-tooltip="Open website"]').get_attribute('href')
        phone_number = driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label^="Phone"]'
        ).get_attribute('data-item-id').replace("phone:tel:", "").strip()
        plus_code = driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label^="Plus code"]'
        ).get_attribute('aria-label').replace("Plus code:", "").strip()
        supports_community = '\n'.join([
            community.text.strip() for community in driver.find_elements(
                By.CSS_SELECTOR, 'div[data-item-id^="place-info-links"]'
            )
        ])
        related_images = [image.get_attribute("src") for image in driver.find_elements(By.CLASS_NAME, "DaSXdd")]
        # Open working hours drop down
        show_working_hours = driver.find_element(
            By.CSS_SELECTOR, 'span[aria-label^="Show open hours"]'
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            show_working_hours)
        show_working_hours.click()
        working_hours = driver.find_element(
            By.CSS_SELECTOR,
            'div[aria-label$="Hide open hours for the week"] table'
        ).text.strip().replace('\u202f', ' ').split("\n")

        # Scrape reviews

    try:
        scroll_end = driver.find_element(By.CSS_SELECTOR, 'div[class^="PbZDve"] > p').text
        if 'end of the list' in scroll_end:
            print('reached end')
            break
    except NoSuchElementException:
        ...
    sleep(.5)


