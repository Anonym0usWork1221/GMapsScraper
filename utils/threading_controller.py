from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.google_maps_scraper import GoogleMaps
from signal import signal, SIGINT, SIGTERM
from threading import Lock, Event
from atexit import register


class FastSearchAlgo:
    def __init__(self,
                 unavailable_text: str = "Not Available", headless: bool = False, wait_time: int = 15,
                 suggested_ext: list = None, output_path: str = "./CSV_FILES", result_range: int = None,
                 workers: int = 1, verbose: bool = True,
                 output_format: str = "CSV",
                 scroll_minutes: int = 1
                 ) -> None:
        if suggested_ext is None:
            suggested_ext = ["contact-us", "contact"]

        self._unavailable_text = unavailable_text
        self._headless = headless
        self._wait_time = wait_time
        self._suggested_ext = suggested_ext
        self._output_path = output_path
        self._result_range = result_range
        self._scroll_minutes = scroll_minutes
        self._verbose = verbose
        self._output_format = output_format

        self._workers = workers
        self._query_list = list()
        self._threads_handlers = list()
        self._print_lock = Lock()
        self._thread_stop_event = Event()
        self._executor = ThreadPoolExecutor(max_workers=self._workers)
        super().__init__()

    def signal_handler(self, sig, frame):
        print('[+] Exiting and releasing memory')
        self._thread_stop_event.set()
        self._executor.shutdown(wait=False)  # Shut down threads immediately

    def fast_search_algorithm(self, query_list: list[str]):
        query_list_range = len(query_list)
        self._query_list = query_list
        signal(SIGINT, self.signal_handler)

        futures = []
        for thread_index in range(self._workers):
            future = self._executor.submit(self._start_scrapper_threads, thread_index, query_list_range)
            futures.append(future)

        register(self.signal_handler, SIGTERM, None)

        for future in as_completed(futures):
            # This will ensure that if an exception occurred in the thread, it will be raised here.
            future.result()

    def _start_scrapper_threads(self, thread_id: int, query_list_range: int) -> None:
        maps_obj = GoogleMaps(unavailable_text=self._unavailable_text, headless=self._headless,
                              wait_time=self._wait_time,
                              output_format=self._output_format,
                              suggested_ext=self._suggested_ext, output_path=self._output_path,
                              print_lock=self._print_lock,
                              result_range=self._result_range, verbose=self._verbose,
                              stop_event=self._thread_stop_event,
                              scroll_minutes=self._scroll_minutes
                              )

        range_calculation = query_list_range / self._workers
        thread_start = thread_id * int(range_calculation)
        thread_end = thread_start + int(range_calculation)

        for thread_index in range(thread_start, thread_end):
            try:
                maps_obj.start_scrapper(self._query_list[thread_index])
            except Exception as e:
                print(f"Exception in thread {thread_id}: {e}")
                continue

    @staticmethod
    def load_query_file(file_name: str):
        try:
            file_data = open(file_name, "r", encoding="utf-8").readlines()
        except (FileNotFoundError, FileNotFoundError):
            return []

        clean_data = []
        for data in file_data:
            clean_data.append(data.strip())

        return clean_data
