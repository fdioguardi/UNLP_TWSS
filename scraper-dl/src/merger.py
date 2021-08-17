class Merger(object):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def merge(self):
        for key in self.source:
            self.destination[key] = self.merge_key(key)

        return self.destination

    def merge_key(self, key):

        if not key in self.destination:
            return self.source[key]

        if self._both_have_dicts_in(key):
            return Merger(self.source[key], self.destination[key]).merge()

        elif self._both_have_lists_in(key):
            return self.merge_lists_in(key)

        elif self._is_one_a_list(key):
            return self.append_to_list(
                *self.identify_list_and_value(
                    self.source[key], self.destination[key]
                )
            )

        elif self.source[key] != self.destination[key]:
            return [self.source[key], self.destination[key]]

        else:  # self.source == destination
            return self.source[key]

    def merge_lists_in(self, key):
        for element in self.source[key]:
            self.destination[key] = self.append_to_list(
                self.destination[key], element
            )

        return self.destination[key]

    def append_to_list(self, list_of_elements, single_element):

        if single_element in list_of_elements:
            pass
        elif isinstance(single_element, dict):
            self.append_dict_to_list(list_of_elements, single_element)
        else:
            list_of_elements.append(single_element)

        return list_of_elements

    def append_dict_to_list(self, list_of_elements, single_element):
        try:
            same_dict = next(
                dictionary
                for dictionary in list_of_elements
                if self.are_names_equal(element, single_element)
            )

            same_element.update(single_element)

        except StopIteration:
            list_of_elements.append(single_element)

        finally:
            return list_of_elements

    def are_names_equal(element, another_element):
        return (
            "name" in element.keys()
            and "name" in another_element.keys()
            and element["name"] == another_element["name"]
        )

    def identify_list_and_value(self, a_value, another_value):
        if isinstance(a_value, list):
            return a_value, another_value
        return another_value, a_value

    def _are_both_same_type(self, key, type):
        return isinstance(self.source[key], type) and isinstance(
            self.destination[key], type
        )

    def _both_have_dicts_in(self, key):
        return self._are_both_same_type(key, dict)

    def _both_have_lists_in(self, key):
        return self._are_both_same_type(key, list)

    def _is_one_a_list(self, key):
        return isinstance(self.source[key], list) ^ isinstance(
            self.destination[key], list
        )
