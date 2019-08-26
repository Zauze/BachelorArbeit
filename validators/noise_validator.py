
from validators.data_label import DataLabel
from validators.data_validator import DataValidator
import enhanced_simple_tree_matching as estm
import re


class NoiseValidator(DataValidator):

    def kill_check(self, node):
        # TODO: can noise be killed?
        return False

    def base_check(self, node):
        # TODO: what is mandatory for noise?
        return True

    def hit_check(self, node):
        ids_classes = [r'nav', r'menue', r'dropdown', r'footer', r'pre-headline', r'(^|\s+)btn(\s+|$)', ]
        tags = ['option', 'nav', 'img', 'picture', 'figure', 'source', 'figure', 'img', 'i']

        # Checking whether defining regex are in class or id
        for reg in ids_classes:
            if 'class' in node.attributes:
                if re.search(reg, node.attributes['class'].lower()) is not None:
                    return True
            if 'id' in node.attributes:
                if re.search(reg, node.attributes['id'].lower()) is not None:
                    return True

        if node.type in tags:
            return True

        if estm.number_of_words(DataValidator.flatten_text(node.text)) == 0:
            return True
        if '©' in DataValidator.flatten_text(node.text):
            return True

        return False

    def score_check(self, node):
        score = 0
        # First Condition: Contains only one word which is not highlighted
        # with <p> or <h> tags
        if estm.number_of_words(DataValidator.flatten_text(node.text)) == 1:
            for tag in ['<p>', '<h>', '<h1>', '<h2>', '<h3>', '<h4>', '<h5>', '<h6>', '<header>']:
                if node.has_tag(tag):
                    score = -1
                    break
            score += 1
        return score

    def get_label(self):
        return DataLabel.NOISE

