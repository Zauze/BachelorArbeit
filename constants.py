from detectors.data_detector import DataLabel
"""
This module contains all the constants
that will be used by other components
"""
# Some initialization variables, which will be set by the main
website = ''
logger = None

# Tags only containing text format features
FORMAT_TAGS = [
        'p',
        'strong',
        'abbr',
        'b',
        'i',
        'em',
        'mark',
        'small',
        'del',
        'ins',
        'sub',
        'sup',
    ]

# Noise tags
NOISE_TAGS = [
    'script',
    'footer',
    'meta',
    'noscript',
    'nav',
    'select',
    'option',
    'input',
    'img',
    'figure',
    'picture',
    'form',
    'source',
    'i'
]
# Header tags
HEADER = ['h', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header']

# Noise IDs and Classes inside node's meta
NOISE_IDS_CLASSES = [
    'footer',
    'menu',
    'option',
    'cookie',
    'navigation',
    '_nav',
    'pre-headline',
    'dropdown',
    'button',
    r'(^|\s+)btn(\s+|$)'    # those denote buttons
]

# Region depths
MIN_REGION_DEPTH = 3
MAX_REGION_DEPTH = 13

# Information count (minimal amount of words in a subtree)
MIN_INFORMATION_COUNT = 2

# This content defines the maximal amount of nodes
# to join as data record
K_VALUE = 5
# A max value for deciding whether two nodes will be seen as equal
THRESHOLD = 0.2

# This constant decides at which modified depth a node is
# denoted as too high to contain a data item
# modified depth: depth counted up if the current node is not a string format type
# (like strong etc.)
MOD_MAX_HEIGHT = 1
# Data attributes to extract from the list page
LABELS = [
        DataLabel.TIME,
        DataLabel.DATE,
        DataLabel.TITLE,
        DataLabel.SHORT_DESC,
        DataLabel.LINK,
        DataLabel.LOCATION,
    ]