
from detectors.data_label import DataLabel
from detectors.data_detector import DataValidator
import tree_processor as tp
import re


class NoiseValidator(DataValidator):

    def base_check(self, node):
        # There is no necessity set for noise
        return True

    def hit_check(self, node):
        keywords = ['©', 'copyright']

        if tp.number_of_words(DataValidator.flatten_text(node.text)) == 0:
            return True
        for kw in keywords:
            if kw in DataValidator.flatten_text(node.text):
                return True

        return False

    def score_check(self, node):
        # This function can be adjusted if required
        score = 0
        return score

    def get_label(self):
        return DataLabel.NOISE

