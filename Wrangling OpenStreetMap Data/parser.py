# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

osm_file = "sample.osm"

def get_element(osm_file, tags=('node', 'way', 'relation')):
    

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def count_tags(filename):
    # Counts the number of top level tags
    tags = defaultdict(int)
    for element in get_element(filename):
        tags[element.tag] += 1
        for child in element:
            tags[child.tag] += 1
    return dict(tags)
    
if __name__ == "__main__":
    pprint.pprint(count_tags(osm_file))