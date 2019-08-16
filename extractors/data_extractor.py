import re
from validators.data_label import DataLabel

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
                # Getting the fitting extractor object
                extractor = DataExtractor.class_lookup(label)()

                # Getting the node for the extractor
                # if there is a hit
                if len(label_dict[label]['hits']) == 1:
                    specific_info = label_dict[label]['hits'][0]
                # else the element with the highest score
                elif len(label_dict[label]['scores']) >= 1:
                    points = []
                    for el in label_dict[label]['scores']:
                        points.append(el[0])
                    index = points.index(max(points))
                    specific_info = label_dict[label]['scores'][index][1]
                # else no information is given
                else:
                    continue
                info_dict.update(extractor.extract(specific_info))
            ret_list.append(info_dict)
        return ret_list

    def extract(self, node):
        raise NotImplementedError('Calling extract from abstract class!')

    def remove_extra_whitespaces(self, text):
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
            (DataLabel.TITLE, ex.title_extractor.TitleExtractor),
            (DataLabel.TIME, ex.time_extractor.TimeExtractor),
            (DataLabel.SHORT_DESC, ex.short_desc_extractor.ShortDescExtractor),
            (DataLabel.LINK, ex.link_extractor.LinkExtractor),
            (DataLabel.DATE, ex.date_extractor.DateExtractor),
            (DataLabel.LOCATION, ex.location_extractor.LocationExtractor)
        ]
        for el in lookup_table:
            if label == el[0]:
                return el[1]
