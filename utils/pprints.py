from threading import Lock, active_count
from psutil import Process
from platform import system as system_platform
from os import system


class PPrints:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

    def __init__(self, print_lock: Lock):
        self._print_lock = print_lock
        self._process = Process()

    @staticmethod
    def unpack_result_indices(results_indices: any([str, list[int, int]]) = "Calculating"):
        try:
            if results_indices.isalpha():
                return f"Results: {results_indices}"
        except AttributeError:
            return f"Total Results: {results_indices[0]}\nCurrent Result Index: {results_indices[1]}"

    @staticmethod
    def clean_terminal():
        if system_platform().lower() == "windows":
            system("cls")
        else:
            system("clear")
        return system_platform()

    def print_with_lock(self, query: str, status: str, mode: str,
                        results_indices: any([str, list[int]]) = "Calculating", output_format: str = "CSV"):
        version = 0.1
        with self._print_lock:
            memory_info = self._process.memory_info()
            current_memory_usage = memory_info.rss / 1024 / 1024  # Convert bytes to megabytes

            results_index_data = self.unpack_result_indices(results_indices=results_indices)
            if active_count() - 1 == 0:
                launched_drivers = 1
            else:
                launched_drivers = active_count() - 1
            print(f"{self.WARNING}Platform: {self.clean_terminal()}\n"
                  f"{self.CYAN}Developer: AbdulMoez\n"
                  f"{self.GREEN}Script Version: {version}\n"
                  f"{self.WARNING}GitHub: github.com/Anonym0usWork1221/GMapsScraper\n"
                  f"{self.BLUE}Query: {query}\n{self.GREEN}Status: {status}\n"
                  f"{self.CYAN}RunningThreads: {active_count()-1}\n{self.BLUE}Mode: {mode}\n"
                  f"{self.GREEN}OutPutFile: {output_format}\n{self.BLUE}{results_index_data}\n"
                  f"{self.GREEN}LaunchedDrivers: {launched_drivers}\n"
                  f"{self.RED}MemoryUsageByScript: {current_memory_usage: .2f}MB\n"
                  f"{self.RED}Warning: Don't open the output file while script is running\n"
                  f"{self.RESET}", end="\r")

