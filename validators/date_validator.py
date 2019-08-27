from logicmachine import *
from validators.data_validator import DataValidator
import enhanced_simple_tree_matching as estm
import functools
import re

class DateValidator(DataValidator):
    hit_labels = [
        'date',
        'datum'
    ]

    sufficient_classes = [
        'month',
        'monat',
        'day',
        'tag',
        'year',
        'jahr'
    ]

    def kill_check(self, node):
        return False

    def base_check(self, node):
        found = False
        if 'class' in node.attributes:
            if DataValidator.in_class_ids(node, DateValidator.hit_labels):
                found = True

        # Regex searching for full dates like 21.07.2019 or 21.07
        if re.search(
                '([0-3]?[0-9]{1})[.:\-\s]+(0[1-9]{1}|1[012]{1})([.:\-\s]+(2[0-9]{3}|[0-1]{1}[0-9]{1})|\s+|$)',
                DataValidator.flatten_text(node.text)
        ):
            found = True

        # Regex searching for date containing month names like 21.August or 21 August
        match_data = re.match('\s*([012]{1}[1-9]{1}|[3]{1}[01]{1})[.:\-\s]+([a-zA-Z]+)', DataValidator.flatten_text(node.text))
        if match_data is not None:
            for group in match_data.groups():
                if group[1].lower() in [
                    'januar',
                    'jan',
                    'februar',
                    'feb',
                    'märz',
                    'april',
                    'apr'
                    'mai',
                    'juni',
                    'jun',
                    'juli',
                    'jul',
                    'august',
                    'aug',
                    'september',
                    'sep',
                    'oktober',
                    'okt',
                    'november',
                    'nov',
                    'dezember',
                    'dez'
                ]:
                    found = True
        if not found:
            return False

        return True

    def hit_check(self, node):
        if node.type in ['time']:
            return True
        return DataValidator.in_class_ids(node, DateValidator.hit_labels)

    def score_check(self, node):
        # Preparations
        score = 0
        weights = [2, 3, 1, 3]
        max_value = functools.reduce((lambda x, y: x + y), weights)
        words = ['am', 'vom', 'bis', 'zum', 'datum']

        # Condition 1: The text has fewer than 15 words
        if estm.number_of_words(DataValidator.flatten_text(node.text)) <= 15:
            score += weights[0]
            # Condition 2. Additionally contains suitable words
            for word in words:
                if word in DataValidator.flatten_text(node.text.lower()):
                    score += weights[1]
                    break
        else:
            # Condition 3: Contains suitable words but has more than 15 words
            for word in words:
                if word in DataValidator.flatten_text(node.text.lower()):
                    score += weights[2]
                    break

        # Condition 4: Contains suitable classes
        if DataValidator.in_class_ids(node, DateValidator.hit_labels):
            score += weights[3]

        return float(score) / float(max_value)

    def get_label(self):
        return DataLabel.DATE
    