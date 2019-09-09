from detectors.data_detector import DataValidator
from detectors.data_label import DataLabel
import tree_processor as tp
import functools
import re


class TitleValidator(DataValidator):
    hit_labels = [
        'headline',
        'title',
        'titel'
    ]

    def base_check(self, node):
        text = DataValidator.flatten_text(node.text)
        if tp.number_of_words(text) > 15:
            return False
        if len(node.get_children()) > 1:
            return False
        return True

    def hit_check(self, node):
        return DataValidator.in_class_ids(node, TitleValidator.hit_labels)

    def score_check(self, node):
        # Preparations
        score = 0
        weights = [2, 3, 2, 2, 2, 1]
        max_value = functools.reduce((lambda x, y: x + y), weights)

        # Condition 1: Contains more uppercase words
        if not DataValidator.contains_more_lower_than(node, 0.5):
            score += weights[0]

        # Condition 2: Contains header
        for tag in ['h', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if node.has_tag(tag):
                score += weights[1]
                break

        # Condition 3: Contains less than 10 words
        if tp.number_of_words(DataValidator.flatten_text(node.text)) <= 10:
            score += weights[2]
            # Condition 4: Contains symbols - and :
            if re.search('[:\-]+', DataValidator.flatten_text(node.text)):
                score += weights[3]

        # Condition 5: Contains a link node
        if node.has_tag('a'):
            score += weights[4]

        # Condition 6: Contains no numbers or slashes
        if re.search('[0-9\/]+', DataValidator.flatten_text(node.text)) is None:
            score += weights[5]

        return float(score) / float(max_value)

    def get_label(self):
        return DataLabel.TITLE
