import os

os.system('python main.py "http://www.grafing.de/index.php?id=0,17"')
#os.system('python main.py "html.html" "https://veranstaltungen.herrsching.de"')

"""
Works:
    - https://www.allgaeu.de/veranstaltung-allgaeu
    - https://veranstaltungen.herrsching.de (location is embedded in the date/time header - as location the description 
    is extracted and the description has more information as it should)
    - 
     
"""