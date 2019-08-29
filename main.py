# -*- coding: iso-8859-1 -*-
from easyhtml import parser
from extractors.data_extractor import DataExtractor
from constants import *
from html_node import HTMLNode
import constants
import easyhtml
import urllib.request
import urllib.error
import validator
import logicmachine
import errors.errors
import data_region_finder
import logging
import sys
import os.path
import yaml

# TODO: check if this is needed
#sys.setrecursionlimit(1000000000)

# Creating the logger
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger = logging.getLogger('Extractor')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
# Making it accessible for every component
constants.logger = logger

# Processing the parameters
if len(sys.argv) == 1:
    # Showing help if no parameter is given
    print(
        "Usage of the Event Extractor:\n"
        "\tpython main.py [link | path_to_html_file website_url]\n"
        "\n"
        "\t1.) provide an URL as argument\n"
        "\t\tOR\n"
        "\t2.) provide a path to a html file together with the URL (required for long description extraction)"
    )
    exit(0)
elif len(sys.argv) == 2:
    # One param -> url
    website = sys.argv[1].strip()
    # Trying to request website and getting the raw html code
    try:
        response = urllib.request.urlopen(website)
    except urllib.error.URLError as e:
        logger.error('Page:"%s" was not found' % website)
        raise e
    # decoding
    source = response.read().decode('utf-8')
elif len(sys.argv) == 3:
    # two params -> html file and url
    if not os.path.isfile(sys.argv[1]):
        logger.error("%s is not recognized as valid file" % sys.argv[1])
    source = open(sys.argv[1], 'r', encoding='utf-8').read()
    website = sys.argv[2]
else:
    logger.error('Wrong amount of parameters provided! Required is either link or '
                 'path to html file with the corresponding url...')
    exit(0)

# Adding to constants to access from everywhere
constants.website = website

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
    # Returning if no html node was found
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

# Creating yaml file for storing
open('output.yaml', 'a').close()
fd = open('output.yaml', 'w')

# Storing information_list to file
yaml.dump(information_list, fd, default_flow_style=False)

# grafing, tutzing, ebersberg, starnberg, bermatingen, allgäu, tvkempten, salem
# working: ebersberg, bermatingen, allgäu, tvkempten, salem, grafing, herrsching, tettnang
# not-working: grafing, salem

# wasserburg hat nicht alle Informationen (zB location fehlen ein paar)