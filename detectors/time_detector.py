from detectors.data_detector import DataValidator
from detectors.data_label import DataLabel
import tree_processor as tp
import functools
import re


class TimeValidator(DataValidator):
    hit_labels = [
        'time',
        'zeit',
        'uhr',
    ]

    def base_check(self, node):
        text = DataValidator.flatten_text(node.text)
        found = False
        if re.search('(\s+|^)(([0-1]{1}[0-9]{1}|2[0-4]{1})[:]+([0-5]{1}[0-9]{1}))(\s+|$)', text) is not None:
            found = True
        if re.search('([0-9]{1}|[0-5]{1}[0-9]{1})\s+uhr', text.lower()) is not None:
            found = True
        return found

    def hit_check(self, node):
        if node.type in ['time']:
            return True
        return DataValidator.in_class_ids(node, TimeValidator.hit_labels)

    def score_check(self, node):
        # Preparations
        score = 0
        weights = [2, 3, 1]
        # 1 gets subtracted because of the else statement
        max_value = functools.reduce((lambda x, y: x + y), weights) - 1
        words = ['von', 'bis', 'ab', 'uhrzeit', 'um']
        
        # Condition 1: contains less than 16 words
        if tp.number_of_words(DataValidator.flatten_text(node.text)) <= 15:
            score += weights[1]
            # Condition 2: combination of 1 and 2
            for word in words:
                if word in DataValidator.flatten_text(node.text.lower()):
                    score += weights[2]
                    break
        else:
            # Condition 3: contains suitable words
            for word in words:
                if word in DataValidator.flatten_text(node.text.lower()):
                    score += weights[0]
                    break
            
        return float(score) / float(max_value)

    def get_label(self):
        return DataLabel.TIME