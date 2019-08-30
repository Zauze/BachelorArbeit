from detectors.data_detector import DataValidator
from detectors.data_label import DataLabel
import functools
import tree_processor as tp
import re


class ShortDescValidator(DataValidator):
    ids_and_classes = [
        'desc',
        'beschreibung',
    ]

    def kill_check(self, node):
        if DataValidator.in_class_ids(node, ShortDescValidator.ids_and_classes):
            return False
        text = DataValidator.flatten_text(node.text)
        if tp.number_of_words(text) < 3:
            return True
        for child in node.get_children():
            if child.has_tag('div') or child.has_tag('span'):
                return True
        return False

    def base_check(self, node):
        found = False
        for tag in ['span', 'div']:
            if node.has_tag(tag):
                found = True
        if tp.number_of_words(DataValidator.flatten_text(node.text)) > 15:
            found = True
        return found

    def hit_check(self, node):
        if DataValidator.in_class_ids(node, ShortDescValidator.ids_and_classes):
            return True
        if tp.number_of_words(DataValidator.flatten_text(node.text)) >= 20:
            return True
        return False

    # Computes how many percent the node fulfills the
    # conditions
    def score_check(self, node):
        # preparations
        score = 0
        weights = [2, 1, 3, 2, 2]
        max_value = functools.reduce((lambda x, y: x * y), weights)
        text = DataValidator.flatten_text(node.text)

        # Condition 1: more than 15 words
        if tp.number_of_words(text) >= 15:
            score += weights[0]

        # Condition 2: Contains quotation marks
        if re.match('".+"', text) is not None:
            score += weights[1]

        # Condition 3: Does not contain any headers
        found = False
        for tag in ['stronger', 'header', 'h', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if node.has_tag(tag):
                found = True
                break
        if not found:
            score += weights[2]

        # Condition 4: Contains more lowercase words than uppercase
        if DataValidator.contains_more_lower_than(node):
            score += weights[3]

        # Condition 5: Contains full stops, exclamation signs,
        #              questions signs, semicolons, colons
        if re.match('[.:;?!]\s+|[.:;?!]$', text):
            score += weights[4]

        # Returning score
        return float(score) / float(max_value)

    def get_label(self):
        return DataLabel.SHORT_DESC

