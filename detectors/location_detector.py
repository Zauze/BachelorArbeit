from detectors.data_label import DataLabel
from detectors.data_detector import DataValidator
import tree_processor as tp
import functools
import re


class LocationValidator(DataValidator):
    # _loc and loc_ are in the list because some words can contain
    # the substring loc in it, for example block
    ids_classes = [
        'loc_',
        '_loc',
        'location',
        'ort',
        'place',
        'stadt',
        'city'
    ]

    key_words = [
        'ort',
        'location'
    ]

    def base_check(self, node):
        text = DataValidator.flatten_text(node.text)
        if tp.number_of_words(text) > 15:
            return False
        if re.search('[\/?!]', text):
            return False
        # Checking the cases
        if DataValidator.contains_more_lower_than(node, (1.0/3.0)):
            return False
        return True

    def hit_check(self, node):
        if DataValidator.in_class_ids(node, LocationValidator.ids_classes):
            return True
        if tp.number_of_words(DataValidator.flatten_text(node.text)) <= 10:
            for word in LocationValidator.key_words:
                reg = '(\s+|^)%s(\s+|:)\s*\S+' % word
                if re.match(reg, DataValidator.flatten_text(node.text).lower()):
                    return True
        return False

    def score_check(self, node):
        # Preparations
        score = 0
        weights = [2, 2, 2, 2]
        max_value = functools.reduce((lambda x, y: x + y), weights)
        text = DataValidator.flatten_text(node.text)

        # Condition 1: has header tags
        found = False
        for tag in ['header', 'h', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if node.has_tag(tag):
                found = True
                break
        if not found:
            score += weights[0]

        # Condition 2: Contains address and house number
        # Regexp for searching for house numbers, allowed are f.e.:
        # Somestreet 12, Somestreet 12a
        # but not:
        # Somestreet 12sometextwithoutanywhitespace
        if re.search('([a-zA-Z]+\s+[0-9]{1,3}\w?\s+|[a-zA-Z]+\s+[0-9]{1,3}\w?$)', text) is not None:
            score += weights[1]

        # Condition 3: Contains postal code(Germany)
        # Regexp for postal code
        if re.search('(\s+[0-9]{5}\s+|\s+[0-9]{5}$)', text) is not None:
            score += weights[2]

        # Condition 4: Contains less than 11 words
        if tp.number_of_words(text) <= 10:
            score += weights[3]

        return float(score) / float(max_value)

    def get_label(self):
        return DataLabel.LOCATION