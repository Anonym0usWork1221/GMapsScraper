from selenium.webdriver.chrome.webdriver import WebDriver
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from re import compile
# from requests import head


class PatternScrapper:

    def __init__(self):
        self._last_opened_handler = None
        self._email_pattern = compile(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)*')
        self._fb_pattern = compile(r'(?:https?://)?(?:www\.)?facebook\.com/\S+')
        self._twitter_pattern = compile(r'(?:https?://)?(?:www\.)?twitter\.com/\S+')
        self._insta_pattern = compile(r'(?:https?://)?(?:www\.)?instagram\.com/\S+')
        self._youtube_pattern = compile(r'(?:https?://)?(?:www\.)?youtube\.com/\S+')
        self._linkedin_pattern = compile(r'(?:https?://)?(?:www\.)?linkedin\.com/\S+')

    """TO DO: Results not correct to some extend"""
    # @staticmethod
    # def check_validation(url_list: list):
    #     valid_urls = []
    #     for url in url_list:
    #         request_response = head(url)
    #         status_code = request_response.status_code
    #         if status_code == 200:
    #             valid_urls.append(url)
    #         elif status_code == 301:
    #             request_response = head(request_response.headers["Location"])
    #             status_code = request_response.status_code
    #             if status_code == 200:
    #                 valid_urls.append(url)
    #     # print(valid_urls)
    #     return valid_urls

    @staticmethod
    def create_urls(site_url: str, url_ext: list):
        # https://www.google.com/something
        site_parser = urlparse(site_url)
        base_url = site_parser.netloc  # www.google.com
        scheme = site_parser.scheme  # https
        if not scheme:
            scheme = "http"

        created_urls = []
        for url in url_ext:
            if scheme + "://" + base_url + "/" == site_url:
                org_url = site_url + url
            else:
                created_urls.append(site_url + url)
                org_url = scheme + "://" + base_url + "/" + url  # https://www.google.com/about

            created_urls.append(org_url)
        return created_urls

    def get_source_code(self, driver: WebDriver, urls: list):
        source_codes = []

        for url in urls:
            driver.execute_script(f'''window.open("{url}", "_blank");''')
            driver.switch_to.window(driver.window_handles[-1])
            source_codes.append(driver.page_source)
            driver.close()
            driver.switch_to.window(self._last_opened_handler)
        return source_codes

    @staticmethod
    def email_decoder(email):
        decoded_mail = ""
        k = int(email[:2], 16)

        for i in range(2, len(email) - 1, 2):
            decoded_mail += chr(int(email[i:i + 2], 16) ^ k)

        return decoded_mail

    def _href_emails(self, soup: BeautifulSoup) -> list:
        email_list = []
        mail_tos = soup.select('a[href]')
        for mail in mail_tos:
            href = mail['href']
            if "email-protect" in href:
                email_list.append(self.email_decoder(href.split("#")[1]))
            elif "mailto" in href:
                email_list.append(href.removeprefix("mailto:").strip())

        return email_list

    def get_pattern_data(self, source_codes: list):
        patterns_data = {"site_email": [], "facebook_links": [], "twitter_links": [], "instagram_links": [],
                         "youtube_links": [], "linkedin_links": []}

        for source in source_codes:
            soup = BeautifulSoup(source, features="lxml", parser="html.parser")

            site_email = [x for x in str(soup) if self._email_pattern.search(x).group()]
            if not site_email:
                href_emails = self._href_emails(soup)
                site_email.extend(href_emails)

            facebook_links = [link['href'] for link in soup.find_all('a', href=self._fb_pattern)]
            twitter_links = [link['href'] for link in soup.find_all('a', href=self._twitter_pattern)]
            instagram_links = [link['href'] for link in soup.find_all('a', href=self._insta_pattern)]
            youtube_links = [link['href'] for link in soup.find_all('a', href=self._youtube_pattern)]
            linkedin_links = [link['href'] for link in soup.find_all('a', href=self._linkedin_pattern)]

            patterns_data["site_email"].extend(site_email)
            patterns_data["facebook_links"].extend(facebook_links)
            patterns_data["twitter_links"].extend(twitter_links)
            patterns_data["instagram_links"].extend(instagram_links)
            patterns_data["youtube_links"].extend(youtube_links)
            patterns_data["linkedin_links"].extend(linkedin_links)
        return patterns_data

    def find_patterns(self, driver: WebDriver, site_url: str, suggested_ext: list, unavailable: str = "Not Available"):
        patterns_data = {"site_email": "", "facebook_links": "", "twitter_links": "", "instagram_links": "",
                         "youtube_links": "", "linkedin_links": ""}

        if site_url == unavailable or suggested_ext == []:
            for key in patterns_data.keys():
                patterns_data[key] = unavailable
            return patterns_data

        valid_urls = self.create_urls(site_url, suggested_ext)
        # self.check_validation(valid_urls)

        self._last_opened_handler = driver.current_window_handle
        try:
            sources = self.get_source_code(driver, valid_urls)
        except Exception:
            for key in patterns_data.keys():
                patterns_data[key] = unavailable
            return patterns_data

        social_data = self.get_pattern_data(sources)

        for key in social_data.keys():
            if not social_data[key]:
                patterns_data[key] = unavailable
            else:
                patterns_data[key] = social_data[key][0]

        return patterns_data


"""Testing samples"""
# if __name__ == '__main__':
#     from selenium.webdriver import Chrome
#     from selenium.webdriver.chrome.service import Service
#     from webdriver_manager.chrome import ChromeDriverManager
#
#     App = PatternScrapper()
#     d = Chrome(service=Service(ChromeDriverManager().install()))
#     print(App.find_patterns(d, site_url="https://husknashville.com/about/", suggested_ext=["about"]))
# print(App.find_patterns(d, site_url="http://gofitnessng.com/contact-us/", suggested_ext=["contact-us", "contact"]))
# print(App.find_patterns(d, site_url="https://octavebytes.com/contact-us/", suggested_ext=["contact-us", "contact"]))
