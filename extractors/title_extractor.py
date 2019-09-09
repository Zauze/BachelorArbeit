from extractors.data_extractor import DataExtractor
import errors.errors
from detectors.data_detector import DataValidator
from detectors.data_label import DataLabel


class TitleExtractor(DataExtractor):
    """
    Extractor class for title
    """
    def extract(self, node):
        if DataLabel.TITLE not in node.data_container['label']['hits']:
            for label in [DataLabel.DATE, DataLabel.TIME]:
                if DataExtractor.is_hit(node, label):
                    return None

        text = DataValidator.flatten_text(node.text)
        return {
            'title': DataExtractor.remove_extra_whitespaces(text).strip()
        }
