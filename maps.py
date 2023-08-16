from webdriver_manager.chrome import ChromeDriverManager
from utils.threading_controller import FastSearchAlgo
from argparse import ArgumentParser
from os.path import isfile
import sys


class GMapsScraper:
    def __init__(self):
        self._args = None

    def arg_parser(self):
        parser = ArgumentParser(description='Command Line Google Map Scraper by Abdul Moez')

        # Input options
        parser.add_argument('-q', '--query-file', help='Path to query file (default: ./queries.txt)', type=str,
                            default="./queries.txt")
        parser.add_argument('-w', '--threads', help='Number of threads to use (default: 1)', type=int, default=1)
        parser.add_argument('-l', '--limit', help='Number of results to scrape (-1 for all results, default: -1)',
                            type=int, default=-1)
        parser.add_argument('-u', '--unavailable-text',
                            help='Replacement text for unavailable information (default: "Not Available")', type=str,
                            default="Not Available")
        parser.add_argument('-bw', '--browser-wait', help='Browser waiting time in seconds (default: 15)', type=int,
                            default=15)
        parser.add_argument('-se', '--suggested-ext',
                            help='Suggested URL extensions to try (can be specified multiple times)', action='append',
                            default=[])
        parser.add_argument('-wb', '--windowed-browser', help='Disable headless mode', action='store_false',
                            default=True)
        parser.add_argument('-v', '--verbose', help='Enable verbose mode', action='store_true')
        parser.add_argument('-o', '--output-folder', help='Output folder to store CSV details (default: ./CSV_FILES)',
                            type=str, default='./CSV_FILES')
        parser.add_argument('-d', '--driver-path',
                            help='Path to Chrome driver (if not provided, it will be downloaded)', type=str,
                            default='')

        # Custom commands for additional help
        parser.add_argument('--help-query-file', action='store_true', help='Get help for specifying the query file')
        parser.add_argument('--help-limit', action='store_true', help='Get help for specifying the result limit')
        parser.add_argument('--help-driver-path', action='store_true', help='Get help for specifying the driver path')

        self._args = parser.parse_args()

    @staticmethod
    def print_query_file_help():
        print("The query file should contain a list of search queries, each query on a separate line.")
        print("For example:")
        print("Pizza restaurants")
        print("Coffee shops")
        print("...")
        sys.exit(0)

    @staticmethod
    def print_limit_help():
        print("Use this option to specify the maximum number of results to scrape.")
        print("Use '-1' to scrape all results.")
        sys.exit(0)

    @staticmethod
    def print_driver_path_help():
        print("If you have a specific Chrome driver path, you can provide it using this option.")
        print("If not provided, the script will attempt to download the driver automatically.")
        print("You can download a compatible driver from https://chromedriver.chromium.org/downloads.")
        sys.exit(0)

    def check_args(self):
        q = self._args.query_file
        if not isfile(q):
            print(f"[-] File not found at path: {q}")
            sys.exit(1)

    def scrape_maps_data(self):
        self.check_args()

        if self._args.help_query_file:
            self.print_query_file_help()

        if self._args.help_limit:
            self.print_limit_help()

        if self._args.help_driver_path:
            self.print_driver_path_help()

        queries_list = FastSearchAlgo.load_query_file(file_name=self._args.query_file)
        threads_limit = min(self._args.threads, len(queries_list))
        limit_results = None if self._args.limit == -1 else self._args.limit

        driver_path = self._args.driver_path
        if not self._args.driver_path:
            try:
                driver_path = ChromeDriverManager().install()
            except ValueError:
                print("[-] Not able to download the driver which is capable with your browser.")
                print("[INFO] Head to this site (https://chromedriver.chromium.org/downloads)"
                      " and find your version driver and pass it with argument -d.")
                exit()

        algo_obj = FastSearchAlgo(
            unavailable_text=self._args.unavailable_text,
            headless=self._args.windowed_browser,
            wait_time=self._args.browser_wait,
            suggested_ext=self._args.suggested_ext,
            output_path=self._args.output_folder,
            workers=threads_limit,
            result_range=limit_results,
            verbose=self._args.verbose,
            driver_path=driver_path
        )

        algo_obj.fast_search_algorithm(queries_list)


if __name__ == '__main__':
    App = GMapsScraper()
    App.arg_parser()
    App.scrape_maps_data()
