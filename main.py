# -*- coding: iso-8859-1 -*-
from easyhtml import parser
from extractors.data_extractor import DataExtractor
from constants import *
from html_node import HTMLNode
from flask import Flask, request
import constants
import easyhtml
import urllib.request
import urllib.error
import data_region_processor
import errors.errors
import data_region_identifier
import logging
import sys
import os.path
import json
import preprocessor

"""
https://grafing.de/index.php?id=0,17  
working fine the most time,
data records are split into several nodes,
because of the path similarity, several paths
are granted with a 2

https://veranstaltungen.tutzing.de/tutzing/?kms=5 :
CANNOT BE BROWSED! MUST BE READ FROM A HTML FILE
 Works fine
 as location the whole header is extracted (with date)
 
https://www.ebersberg.de/freizeit-tourismus/veranstaltungen/highlights.html
USES A NESTED HTML TAG WHICH IS ONLY NON EMPTY WHEN BROWSED BY BROWSER - HTML FILE MUST BE
PROVIDED FOR EXTRACTION
title is wrong - to much information is extracted because of bad annotation

https://veranstaltungen.meinestadt.de/starnberg
Works fine, except of title is labeled as location

https://www.bermatingen.de/index.php?id=344
Works fine

https://www.allgaeu.de/veranstaltung-allgaeu
Works fine

https://www.tvkempten.de/termine.html#sub-menu
NEEDS TO BE LOADED FROM A HTML FILE
Works fine, except description is taking too much information

https://www.salem-baden.de/index.php?id=378&publish[calendarViewType]=classic
NEEDS TO BE LOADED FROM A HTML FILE SINCE FILTERS NOT SET
short desc struggles because if not given the organizer is marked as short desc
otherwise there are two labeled nodes containing the keyword 'description' and the
first is just the pseudo-button with "Mehr informationen"



"""


# salem
# working: ebersberg, bermatingen, allgäu, tvkempten, salem, grafing, herrsching, tettnang
# not-working: grafing, salem

# wasserburg hat nicht alle Informationen (zB location fehlen ein paar)



main = Flask(__name__)

# Creating the logger
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger = logging.getLogger('Extractor')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
# Making it accessible for every component
constants.logger = logger


@main.route("/daex")
def run():
    website = request.args.get('url')
    html_file = request.args.get('html')
    out_file = request.args.get('file')
    logger.info("Starting Data Extractor with the url: %s the html file: %s and output file: %s" % (website, html_file, out_file))
    if website is None and html_file is None:
        # Showing help if no parameter is given
        logger.error("Not enough arguments provided - returning...")
        return(
            "Usage of the Event Extractor: <br>"
            "\tpython main.py [link | path_to_html_file website_url]<br>"
            "<br>"
            "\t1.) provide an URL as argument<br>"
            "\t\tOR<br>"
            "\t2.) provide a path to a html file together with the URL (required for long description extraction)"
        )
    elif website is not None and html_file is None:
        # Trying to request website and getting the raw html code
        try:
            response = urllib.request.urlopen(website)
        except urllib.error.URLError as e:
            logger.error('Page:"%s" was not found' % website)
            raise e
        # decoding (in some cases utf-8 failes)
        try:
            source = response.read().decode('utf-8')
        except:
            source = response.read().decode('latin-1')

    elif html_file is not None:
        if not os.path.isfile(html_file):
            logger.error("%s is not recognized as valid file" % sys.argv[1])
        source = open(html_file, 'r', encoding='utf-8').read()

    # Adding to constants to access from everywhere
    constants.website = website

    logger.debug("Parsing webpage")
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
        raise errors.errors.NotFoundError('No html tag node was found!')

    # Transforming the dom tree into the built in data objects
    # of HTMLNodes
    dom_tree = HTMLNode(html_object, 0)

    logger.debug("Running preprocessing")
    # Preprocess the DOM tree
    preprocessor.preprocess(dom_tree)

    logger.debug("Identifying data regions")
    # Finding data regions
    data_region_identifier.find_data_regions(dom_tree, K_VALUE, THRESHOLD)

    # Extracting data regions
    data_regions = data_region_identifier.extract_data_regions(dom_tree)

    logger.debug("Validating candidates")
    # Validating the data regions and removing the invalid ones
    remove_list = []
    for region in data_regions:
        if not data_region_processor.validate_data_region(region):
            remove_list.append(region)
        else:
            region.update()
    for el in remove_list:
        data_regions.remove(el)

    logger.debug("Determining main data region")
    # Getting the main data region
    main_region = data_region_processor.process_data_regions(data_regions)

    if main_region is None:
        return("No information was extracted since no regions were found")

    logger.debug("Extracting information")
    # Extract the information from the data records
    information_list = DataExtractor.extract_data_records(main_region)

    logger.debug("Saving information to file")
    # Creating yaml file for storing
    out_file = out_file or 'output.yaml'
    open(out_file, 'w').close()

    # Dumping information into a JSON file
    with open(out_file, 'w') as fd:
        json.dump(information_list, fd)
    return("Extracted information saved to %s" % (os.path.dirname(os.path.realpath(__file__)) + "/" + out_file))


if __name__ == "__main__":
    main.run(debug=True)
