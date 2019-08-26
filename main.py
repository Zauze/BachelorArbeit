# -*- coding: iso-8859-1 -*-
from easyhtml import parser
from extractors.data_extractor import DataExtractor
from HTML_Tree import HTMLNode
import easyhtml
import urllib.request
import urllib.error
import validator
import logicmachine
import errors.errors
import data_region_finder
import logging
import sys
sys.setrecursionlimit(1000000000)

# Important constants and variables
# This content defines the maximal amount of nodes
# to join as data record
K_VALUE = 5
# A max value for deciding whether two nodes will be seen as equal
THRESHOLD = 0.2

# Creating the logger
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger = logging.getLogger('Main')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# TODO: Getting website from command line
website = 'https://grafing.de/index.php?id=0,17'
website = 'https://veranstaltungen.meinestadt.de/salem-baden'
website = 'https://www.ueberlingen-bodensee.de/ueberlingen/event/search?reset=1'


website = 'https://www.allgaeu.de/veranstaltung-allgaeu'



# Trying to request website and getting the raw html code
try:
    response = urllib.request.urlopen(website)
except urllib.error.URLError as e:
    logger.error('Page:"%s" was not found' % website)
    raise e
# decoding for every language
source = response.read().decode('latin-1')

# TODO: remove this
#source = open('html.html', 'r', encoding='utf-8').read()

# Transforming the raw html string into a dom tree
dom_parser = parser.DOMParser()
dom_parser.feed(str(source))
document = dom_parser.get_dom()

# Finding the html node
html_object = None
for node in document.elements:
    if isinstance(node, easyhtml.dom.HTMLTag):
        if node.tag_name == 'html':
            html_object = node
            break
if html_object is None:
    raise errors.errors.NotFoundError('No html node was found!')

# Transforming the dom tree into the built in data objects
# of HTMLNodes
dom_tree = HTMLNode(html_object, 0)

# Preprocess the DOM tree
validator.preprocess(dom_tree)

# Finding data regions
data_region_finder.find_data_regions(dom_tree, K_VALUE, THRESHOLD)

# Extracting data regions
data_regions = data_region_finder.extract_data_regions(dom_tree)

# Validating the data regions and removing the invalid ones
remove_list = []
for region in data_regions:
    if not validator.validate_data_region(region):
        remove_list.append(region)
    else:
        region.update()
for el in remove_list:
    data_regions.remove(el)

# Getting the main data region
main_region = logicmachine.process_data_regions(data_regions)

# Extract the information from the data records
information_list = DataExtractor.extract_data_records(main_region)

# TODO: continue here
raise NotImplementedError('Code not implemented yet')

# grafing, tutzing, ebersberg, starnberg, bermatingen, allgäu, tvkempten, salem
# working: ebersberg, bermatingen, allgäu, tvkempten, salem, grafing, herrsching, tettnang
# not-working: grafing, salem

# wasserburg hat nicht alle Informationen (zB location fehlen ein paar)