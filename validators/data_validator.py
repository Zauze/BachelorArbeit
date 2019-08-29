from validators.data_label import DataLabel
import re


class DataValidator:

    def run_checks(self, node):
        if self.kill_check(node):
            return None
        if not self.base_check(node):
            return DataLabel.UNKNOWN
        if self.hit_check(node):
            return self.get_label()
        return self.score_check(node), self.get_label()

    def kill_check(self, node):
        return NotImplementedError('calling kill_check function from abstract class')

    def base_check(self, node):
        return NotImplementedError('calling base_check function from abstract class')

    def hit_check(self, node):
        return NotImplementedError('calling hit_check function from abstract class')

    def score_check(self, node):
        return NotImplementedError('calling score_check function from abstract class')

    def get_label(self):
        return NotImplementedError('calling get_label function from abstract class')

    @staticmethod
    def in_class_ids(node, words):
        """
        Checks if substrings in the class or id string,
        return a boolean value

        :param HTMLNode node:
        :param arr of str words:
        :return: bool
        """
        for word in words:
            if 'class' in node.attributes and word in node.attributes['class']:
                return True
            if 'id' in node.attributes and word in node.attributes['id']:
                return True
        return False

    @staticmethod
    def contains_more_lower_than(node, percentage = 0.5):
        """
        Checks if more lower than uppercase words
        are contained in the node's text

        :param HTMLNode node: the node to check
        :param float percentage: the wanted percentage
        :return: bool
        """
        text = DataValidator.flatten_text(node.text)
        words = re.findall('[^\s]+', text)
        words_counter = 0.0
        capital_words = 0.0
        for word in words:
            if not word[0].isdigit():
                words_counter += 1
                if word[0].isupper():
                    capital_words += 1
        if words_counter != 0:
            if (capital_words / words_counter) > percentage:
                return False
            else:
                return True

    @staticmethod
    def flatten_text(text):
        return re.sub('<\/?[^<>]+>', '', text)
