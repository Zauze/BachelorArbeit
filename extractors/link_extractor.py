from extractors.data_extractor import DataExtractor


class LinkExtractor(DataExtractor):
    """
    Extractor class for links
    """
    def extract(self, node):
        if 'href' in node.attributes:
            return {
                'link': node.attributes['href']
            }
        else:
            return {
                'link': None
            }
