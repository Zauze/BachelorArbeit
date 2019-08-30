import re
from detectors.data_label import DataLabel
import data_region_processor


class DataExtractor:
    """
    Abstract class for each specific data extractor
    """
    @staticmethod
    def extract_data_records(main_region):
        """
        Extracts information for each data record
        :param HTMLNode main_region:
        :return: list of dicts : list with the extracted data
        """
        ret_list = []
        for record in main_region.get_children():
            label_dict = record.data_container['label_dict']
            info_dict = {}
            for label in label_dict:
                if label == DataLabel.NOISE:
                    continue
                # Looking for similarities
                data_region_processor.check_paths(main_region, label)
                # Getting the fitting extractor object
                extractor = DataExtractor.class_lookup(label)()

                # Getting the node for the extractor
                # if there is a hit
                if len(label_dict[label]['hits']) == 1:
                    specific_info = extractor.extract(label_dict[label]['hits'][0])
                # else the element with the highest score
                elif len(label_dict[label]['scores']) >= 1:
                    label_dict[label]['scores'].sort(key=lambda x: x[0], reverse=True)
                    for el in label_dict[label]['scores']:
                        specific_info = extractor.extract(el[1])
                        if specific_info is not None:
                            # This is done for the criterion of exclusion to work
                            # also for non-hits
                            el[1].data_container['label']['hits'].append(label)
                            break
                # else no information is given
                else:
                    continue
                if specific_info is not None:
                    info_dict.update(specific_info)

            # Long Description Extraction
            if 'link' in info_dict and info_dict['link'] is not None:
                extractor = DataExtractor.class_lookup(DataLabel.LONG_DESC)()
                specific_info = extractor.extract(info_dict['link'])
                info_dict.update(specific_info)
            # Appending to the main information dict
            ret_list.append(info_dict)
        return ret_list

    @staticmethod
    def extract(self, node):
        raise NotImplementedError('Calling extract from abstract class!')

    @staticmethod
    def remove_extra_whitespaces(text):
        """
        Removes extra and trailing whitespaces in a string
        :param str text: the text to process
        :return: str
        """
        if text == '':
            return text

        lines = text.splitlines()
        for index in range(len(lines)):
            words = re.findall('[^\s]+', lines[index])
            line = ''
            if len(words) == 0:
                continue
            for word in words[0:-1]:
                line += word + ' '
            lines[index] = line + words[-1]
        new_text = lines[0]
        new_text += "\n".join(lines[1:])
        return new_text

    @staticmethod
    def class_lookup(label):
        import extractors as ex
        import extractors.location_extractor
        import extractors.link_extractor
        import extractors.short_desc_extractor
        import extractors.long_desc_extractor
        import extractors.time_extractor
        import extractors.title_extractor
        import extractors.date_extractor
        """
        Returns the fitting extraction class,
        given the label
        :param DataLabel label:
        :return: DataExtractor class
        """
        lookup_table = [
            (DataLabel.DATE, ex.date_extractor.DateExtractor),
            (DataLabel.TIME, ex.time_extractor.TimeExtractor),
            (DataLabel.TITLE, ex.title_extractor.TitleExtractor),
            (DataLabel.SHORT_DESC, ex.short_desc_extractor.ShortDescExtractor),
            (DataLabel.LINK, ex.link_extractor.LinkExtractor),
            (DataLabel.LOCATION, ex.location_extractor.LocationExtractor),
            (DataLabel.LONG_DESC, ex.long_desc_extractor.LongDescExtractor)
        ]
        for el in lookup_table:
            if label == el[0]:
                return el[1]

    @staticmethod
    def is_hit(node, label, n=2):
        if n == 0:
            return False
        if 'label' in node.data_container:
            if label in node.data_container['label']['hits']:
                return True
        else:
            return False

        return DataExtractor.is_hit(node.parent, label, n-1)
