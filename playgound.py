from easyhtml import parser
from easyhtml import dom
import HTML_Tree
import enhanced_simple_tree_matching as estm
import data_region_finder
import validator
import validators.data_validator
import partial_tree_alignment
import logicmachine
from validators.data_label import DataLabel
import sys
import os
from extractors.data_extractor import DataExtractor
dir_path = os.path.dirname(os.path.realpath(__file__))

sys.path.append(dir_path)


def get_depth(node):
    depth = 0
    if hasattr(node, 'elements') and len(node.elements) > 0:
        for el in node.elements:
            if type(el) == dom.HTMLComment:
                continue
            else:
                el_depth = get_depth(el)
                if el_depth > depth:
                    depth = el_depth
        depth += 1
    return depth




html = open('html_1.html', 'r').read()
dom_parser = parser.DOMParser()
dom_parser.feed(html)
document = dom_parser.get_dom()
node = HTML_Tree.HTMLNode(document.elements[0], 0)


# Here the execution starts
html = open('html_1.html', 'r')
dom_parser = parser.DOMParser()

dom_parser.feed(html.read())

document = dom_parser.get_dom()

tree = HTML_Tree.HTMLNode(document.elements[0], 0)
#tree = validator.preprocess(tree)

a = data_region_finder.find_data_regions(tree, 5, 0.2)
regions = data_region_finder.extract_data_regions(tree)
remove =[]
for region in regions:
    if not validator.validate_data_region(region):
        remove.append(region)
for el in remove:
    regions.remove(el)

main_region = logicmachine.process_data_regions(regions)

records = DataExtractor.extract_data_records(main_region)

a = 10

b = 10

