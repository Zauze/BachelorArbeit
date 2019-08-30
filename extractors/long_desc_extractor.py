import extractors.data_extractor as de
import data_region_identifier


class LongDescExtractor(de.DataExtractor):
    """
    Extractor class for long descriptions
    needs link to a detailed page
    """

    def extract(self, link):
        detailed_page = data_region_identifier.process_link(link)
        if detailed_page is None:
            return {
                'long_desc': None
            }
        main_text_list = data_region_identifier.main_text_extraction(detailed_page)
        text = ""
        for el in main_text_list:
            text += el.get_full_text()
        return {
            'long_desc': text
        }