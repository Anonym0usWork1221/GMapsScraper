from threading import Lock
from csv import DictWriter
from os.path import isfile


class CSVCreator:
    def __init__(self, file_lock: Lock, output_path: str = "./CSV_FILES"):
        self._output_path = output_path
        self._file_lock = file_lock

    def create_csv(self, list_of_dict_data: list[dict]):
        with self._file_lock:
            file_name = "google_maps_data.csv"
            _isheader_file = False
            if not isfile(self._output_path + "/" + file_name):
                _isheader_file = True

            if _isheader_file:
                file_handler = open(self._output_path + "/" + file_name, "w", newline="", encoding="utf-8-sig")
            else:
                file_handler = open(self._output_path + "/" + file_name, "a", newline="", encoding="utf-8-sig")

            writer = DictWriter(file_handler, fieldnames=list_of_dict_data[0].keys(), extrasaction='ignore')
            if _isheader_file:
                writer.writeheader()

            writer.writerows(list_of_dict_data)
            file_handler.close()
