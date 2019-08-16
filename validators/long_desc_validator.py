from logicmachine import *
from validators.data_validator import DataValidator
from validators.data_label import DataLabel
import enhanced_simple_tree_matching as estm
import re


class LongDescValidator(DataValidator):
    ids_and_classes = [
        'desc',
        'beschreibung',
    ]

    def kill_check(self, node):
        text = DataValidator.flatten_text(node.text)
        if estm.number_of_words(text) < 15:
            return True
        return False

    def base_check(self, node):
        # Checking the cases
        words = re.findall('[^\s]+', DataValidator.flatten_text(node.text))
        words_counter = 0.0
        capital_words = 0.0
        for word in words:
            if not word[0].isdigit():
                words_counter += 1
                if word[0].isupper():
                    capital_words += 1
        if words_counter != 0:
            if (capital_words / words_counter) > 0.5:
                return False
        return True

    def hit_check(self, node):
        text = DataValidator.flatten_text(node.text)
        if estm.number_of_words(text) >= 30:
            return True
        if DataValidator.in_class_ids(node, LongDescValidator.ids_and_classes):
            return True
        return False

    def score_check(self, node):
        score = 0
        text = DataValidator.flatten_text(node.text)
        if estm.number_of_words(text) >= 20:
            score += 1
        found = False
        for tag in ['p', 'header', 'h', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if node.has_tag(tag):
                found = True
                break
        if not found:
            score += 1
        return score

    def get_label(self):
        return DataLabel.LONG_DESC
