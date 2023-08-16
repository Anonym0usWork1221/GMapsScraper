from collections import OrderedDict


class DictCleaner:
    def __init__(self, unavailable_data: str = "Not Available"):
        self._unavailable_data = unavailable_data

    @staticmethod
    def _unique_repeating_sets(output_data_dict_list: list[dict]) -> tuple[set, set]:
        unique_keys = set()
        repeating_keys = set()

        for data_dict in output_data_dict_list:
            unique_keys.update(data_dict.keys())
            for key in data_dict.keys():
                if sum(1 for x in output_data_dict_list if key in x) > 1:
                    repeating_keys.add(key)

        return unique_keys, repeating_keys

    def _dict_cleaner(self, output_data_dict_list: list[dict], unique_keys: set, repeating_keys: set) -> list[dict]:

        final_data = []
        for data_dict in output_data_dict_list:
            ordered_dict = OrderedDict()
            for key in unique_keys:
                if key not in data_dict:
                    ordered_dict[key] = self._unavailable_data
                elif key in repeating_keys:
                    ordered_dict[key] = f"{key}_{data_dict[key]}"
                else:
                    ordered_dict[key] = data_dict[key]
            final_data.append(dict(ordered_dict))
        return final_data

    def start_cleaning_dict_data(self, dict_list: list[dict]) -> list[dict]:
        unique_keys, repeating_keys = self._unique_repeating_sets(dict_list)
        cleaned_data_list = self._dict_cleaner(dict_list, unique_keys, repeating_keys)
        return cleaned_data_list

