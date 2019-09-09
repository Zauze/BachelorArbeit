from extractors.data_extractor import DataExtractor
import errors.errors
from detectors.data_detector import DataValidator
import re


class TimeExtractor(DataExtractor):
    """
    Extractor class to extract time
    """
    # TODO: 09.01.2019 09:20 Uhr - 12.11.2019 12:12 Uhr is not functioning properly!
    def extract(self, node):
        """
        Actual extraction function
        :param HTMLNode node: the node where to extract from
        :return: dict : containing time
        """
        text = DataValidator.flatten_text(node.text)
        ret_info = {
            'hour': None,
            'minutes': None
        }
        # Those regex are very strict, no checks needed when extracting
        # Matches strings like 19:15, 12:00, 09:23
        reg_full_time = r'(\s+|^)(([0-1]{1}[0-9]{1}|2[0-4]{1})[:]+([0-5]{1}[0-9]{1}))(\s+|$)'
        # Matches strings like 18:12 uhr
        reg_part_time = r'(\s+|^)(0?[0-9]{1}|1[0-9]{1}|2[0-4]{1})([:](0[0-9]{1}|[1-5]{1}[0-9]{1})|\s*)' \
                        r'\s+uhr'
        # Matches strings like 12 - 19 uhr, 23 bis 2 uhr
        re_part_time_hours = r'(\s+|^)([01]{1}[0-9]{1}|2[0-4]{1})\s*([-:]{1}|bis)\s*' \
                             r'([01]{1}[0-9]{1}|2[0-4]{1})\s+uhr'
        # Matches 00 to 59
        reg_optional_minutes = r'^\s+([0-5]{1}[0-9]{1})(\s+|$)'

        # Those regex are much more loose and additional checks
        reg_loose = r'(\s+|^)((0?[0-9]{1}|1[0-9]{1}|2[0-4]{1})\.([0-5]{1}[0-9]{1}))(-|\s+|$)'

        if re.search(reg_full_time, text) is not None:
            match = re.findall(reg_full_time, text)
            ret_info['hour'] = match[0][2]
            ret_info['minutes'] = match[0][3]
        elif re.search(re_part_time_hours, text.lower()) is not None:
            match = re.findall(re_part_time_hours, text.lower())
            ret_info['hour'] = match[0][1]
            ret_info['minutes'] = '00'
        elif re.search(reg_part_time, text.lower()) is not None:
            match = re.findall(reg_part_time, text.lower())
            ret_info['hour'] = match[0][1]
            if re.match(reg_optional_minutes, match[0][3]):
                match = re.findall(reg_optional_minutes, match[0][3])
                ret_info['minutes'] = match[0][0]
            else:
                ret_info['minutes'] = '00'
        elif re.search(reg_loose, text):
            match = re.findall(reg_loose, text)
            for item in match:
                time = item[1]
                prefix = re.findall('(.+)%s' % time, text)[0]
                prefix_words = re.findall('([^\s]+)', prefix)
                # checking up to 3 words before the time
                for i in range(1, 4):
                    try:
                        allowed = [ '(\s+|^)von', '(\s+|^)ab', '(\s+|^)um']
                        for reg in allowed:
                            if re.search(reg, prefix_words[-1*i], flags=re.IGNORECASE) is not None:
                                ret_info['hour'] = item[2]
                                ret_info['minutes'] = item[3]
                                return ret_info
                    except IndexError:
                        break
        return {
            'time': ("%s:%s" % (ret_info['hour'], ret_info['minutes']))
        }
