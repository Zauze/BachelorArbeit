import re
import extractors as ex
import extractors.data_extractor as de
from detectors.data_detector import DataValidator
from detectors.data_label import DataLabel


class LocationExtractor(ex.data_extractor.DataExtractor):

    def extract(self, node):
        # Only check the other labels, if node does not contains
        # a hit for location
        if DataLabel.LOCATION not in node.data_container['label']['hits']:
            for label in [DataLabel.DATE, DataLabel.TIME, DataLabel.TITLE]:
                if de.DataExtractor.is_hit(node, label):
                    return None

        text = DataValidator.flatten_text(node.text)
        text = self.remove_extra_whitespaces(text)
        text = re.sub('.+:', '', text)
        return {
            'location': text.strip()
        }

