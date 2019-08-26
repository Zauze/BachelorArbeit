from extractors.data_extractor import DataExtractor
import errors.errors
from validators.data_validator import DataValidator
from validators.data_label import DataLabel


class TitleExtractor(DataExtractor):
    """
    Extractor class for title
    """
    def extract(self, node):
        for label in [DataLabel.DATE, DataLabel.TIME]:
            if DataExtractor.is_hit(node, label):
                return None

        text = DataValidator.flatten_text(node.text)
        return {
            'title': self.remove_extra_whitespaces(text)
        }
