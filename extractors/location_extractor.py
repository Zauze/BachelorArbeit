import re
import extractors as ex
import extractors.data_extractor
from validators.data_validator import DataValidator
from validators.data_label import DataLabel


class LocationExtractor(ex.data_extractor.DataExtractor):

    def extract(self, node):
        for label in [DataLabel.DATE, DataLabel.TIME, DataLabel.TITLE]:
            if label in node.data_container['label']['hits']:
                return {
                    'location': None
                }

        text = DataValidator.flatten_text(node.text)
        text = self.remove_extra_whitespaces(text)
        text = re.sub('.+:', '', text)
        return {
            'location': text
        }

