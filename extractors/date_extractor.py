from extractors.data_extractor import DataExtractor
import errors.errors
from validators.data_validator import DataValidator
import re
import datetime


class DateExtractor(DataExtractor):
    """
    Extractor class for date
    """
    def extract(self, node):
        if node.identification == 369:
            a = 10
        text = DataValidator.flatten_text(node.text)
        date_info = {
          'day': None,
          'month': None,
          'year': None
        }
        # Finds date, which contains only numbers, like 21.07.19 or 21.07
        reg_number_date = r'(\s+|^)([0-3]?[0-9]{1})[.:\-\s]+(0[1-9]{1}|1[012])([.:\-\s]+(2[0-9]{3}|' \
                          r'[0-1]{1}[0-9]{1})|\s+|$)'
        reg_full_month = r'(\s+|^)([012]{1}[1-9]{1}|[3]{1}[01]{1})[.:\-\s]+([a-zA-Z]+)(.+)'

        match_year = None

        if re.search(reg_number_date, text):
            match = re.findall(reg_number_date, text)
            date_info['day'] = match[0][1]
            date_info['month'] = match[0][2]
            match_year = match[0][4]
        elif re.search(reg_full_month, text):
            match = re.findall(reg_full_month, text)
            date_info['day'] = match[0][1]
            month = self.month_lookup(match[0][2])
            if month is None:
                raise errors.errors.NotFoundError('Month was not found while date extraction')
            date_info['month'] = month
            if re.search('^[\s:.\-]+(2[0-9]{3}|[0-1]{1}[0-9]{1})(\s+|$)', match[0][3]):
                match_year = re.findall('^[\s:.\-]+(2[0-9]{3}|[0-1]{1}[0-9]{1})(\s+|$)', match[0][3])[0][0]
        else:
            for child in node.get_children():
                if 'class' in child.attributes:
                    if 'day' in child.attributes['class']:
                        date_info['day'] = child.text.strip()
                    if 'month' in child.attributes['class']:
                        date_info['month'] = self.month_lookup(child.text.strip())
                    if 'year' in child.attributes['class']:
                        date_info['year'] = child.text.strip()

        if match_year is None:
            date_info['year'] = datetime.datetime.now().year
        elif len(match_year) == 2:
            try:
                date_info['year'] = '20' + match_year
            except:
                a = 10
        elif len(match_year) == 4:
            date_info['year'] = match_year
        else:
            raise errors.errors.NotFoundError('The year was not found while date extraction')

        return date_info


    def month_lookup(self, text):
        """
        Povides a lookup table to get the month
        number of the given month string
        :param text: month string
        :return: str or None
        """
        lookup_table = [
            ('januar', '01'),
            ('jan', '01'),
            ('februar', '02'),
            ('feb', '02'),
            ('märz', '03'),
            ('april', '04'),
            ('apr', '04'),
            ('mai', '05'),
            ('juni', '06'),
            ('jun', '06'),
            ('juli', '07'),
            ('jul', '07'),
            ('august', '08'),
            ('aug', '08'),
            ('september', '09'),
            ('sep', '09'),
            ('oktober', '10'),
            ('okt', '10'),
            ('november', '11'),
            ('nov', '11'),
            ('dezember', '12'),
            ('dez', '12'),
                ]
        text = text.strip()

        for el in lookup_table:
            if el[0] == text.lower():
                return el[1]
        return None