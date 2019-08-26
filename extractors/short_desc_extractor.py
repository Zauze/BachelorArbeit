from extractors.data_extractor import DataExtractor
import errors.errors
from validators.data_validator import DataValidator
from validators.data_label import DataLabel

class ShortDescExtractor(DataExtractor):
    """
    Extractor class for short descriptions
    """
    def extract(self, node):
        if DataLabel.SHORT_DESC not in node.data_container['label']['hits']:
            for label in [DataLabel.DATE, DataLabel.TIME, DataLabel.TITLE]:
                if DataExtractor.is_hit(node, label):
                    return None

        text = DataValidator.flatten_text(node.text)
        return {
            'short_description': self.remove_extra_whitespaces(text).strip()
        }