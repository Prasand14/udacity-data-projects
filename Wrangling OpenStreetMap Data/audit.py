# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint

filename = "sample.osm"

def get_element(osm_file, tags=('node', 'way', 'relation')):
    

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
    
def street_name(element):
    #Checks if the key is a street name
    return (element.attrib['k'] in ['addr:street', 'addr:full'])
    
def is_city_name(elem):
    #Checks if the key is the city name
	return (elem.attrib['k'] == "addr:city")

def is_postal_code(elem):
    #Checks if the key is a postal code
    return (elem.attrib['k'] == "addr:postcode")

def audit_street(osm_file):
    counts = defaultdict(int)
    names = []
    for element in get_element(osm_file):
        if element.tag in ["node", "way", "relation"]:
            for tag in element.iter("tag"):
                if street_name(tag):
                    if tag.attrib['v']:
                        #Getting counts of addr:street keys
                        counts[tag.attrib['k']] += 1
                        #Storing values of addr:street tags
                        names.append([tag.attrib['v']])
    return dict(counts), names

#unpacks the count and the key values
counts, names = audit_street(filename)    

pprint.pprint(names)
print "The number of 'addr:street': {}".format(counts['addr:street'])

def audit_rest(osm_file):
    #audits city name and postalcodes
    city_name = defaultdict(int)
    postal_codes = defaultdict(int)
    for elem in get_element(osm_file):
        if elem.tag in ["node", "way", "relation"]:
            for tag in elem.iter("tag"):
                if is_city_name(tag):
                    city_name[tag.attrib['v']] += 1
                elif is_postal_code(tag):
                    postal_codes[tag.attrib['v']] += 1                                    
    return city_name, postal_codes

city_name, postal_codes = audit_rest(filename)

pprint.pprint(city_name)
pprint.pprint(postal_codes)    