from detectors.data_detector import DataValidator
from detectors.data_label import DataLabel


class LinkValidator(DataValidator):

    def kill_check(self, node):
        if node.type != 'a':
            return True
        return False


    def base_check(self, node):
        return True


    def hit_check(self, node):
        return False


    def score_check(self, node):
        # TODO: Check if there can be any score check
        score = 1.0
        return score


    def get_label(self):
        return DataLabel.LINK
