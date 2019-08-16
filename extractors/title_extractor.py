from extractors.data_extractor import DataExtractor
import errors.errors
from validators.data_validator import DataValidator


class TitleExtractor(DataExtractor):
    """
    Extractor class for title
    """
    def extract(self, node):
        text = DataValidator.flatten_text(node.text)
        return {
            'title': self.remove_extra_whitespaces(text)
        }
