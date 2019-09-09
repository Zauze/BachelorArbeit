from detectors.data_detector import DataValidator
from detectors.data_label import DataLabel


class LinkValidator(DataValidator):

    def base_check(self, node):
        if node.type != 'a':
            return False
        return True

    def hit_check(self, node):
        return False

    def score_check(self, node):
        score = 1.0
        return score

    def get_label(self):
        return DataLabel.LINK
