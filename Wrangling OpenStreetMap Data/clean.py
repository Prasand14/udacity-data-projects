# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET

filename = "sample.osm"

def get_element(osm_file, tags=('node', 'way', 'relation')):
    

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def street_name(element):
    return (element.attrib['k'] == 'addr:street')
    
def city_name(element):
    return (element.attrib['k'] == 'addr:city')

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")
            
def clean_up(osm_file):
    for element in get_element(osm_file):
        for tag in element.iter("tag"):
            if street_name(tag):
                if ',' in tag.attrib['v']:
                    #changes addr:street to addr:full
                    k = tag.attrib['k'].split(':', 1)
                    k[1] = 'full'
                    tag.attrib['k'] = ':'.join(k)
                    return tag.attrib['k']

                    #Cleans the city name

                if tag.attrib['v'] != "Hyderabad":
                    tag.attrib['v'] = "Hyderabad"
                    return tag.attrib['v']

                    #Cleans postal codes

                if is_postal_code(tag):
                    if tag.attrib['v'] in ['500 032','500 081', '500 095']:
                        k = tag.attrib['v'].split(' ', 1)
                        tag.attrib['v'] = ''.join(k)
                        return tag.attrib['v']
                    
                    if tag.attrib['v'] == '996544':
                        tag.attrib['v'] = '500001'
                        return tag.attrib['v']
                    
                    if len(tag.attrib['v']) != 6:
                        tag.attrib['v'] = '500001'
                        return tag.attrib['v']
                     
            

clean_up(filename)                  


