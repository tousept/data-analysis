#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if the second level tag "k" value contains problematic characters, it should be ignored
- if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if the second level tag "k" value does not start with "addr:", but contains ":", you can
  process it in a way that you feel is best. For example, you might split it into a two-level
  dictionary like with "addr:", or otherwise convert the ":" to create a valid key.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def isfloat(value):
    try:
        float(value)    
        return True
    except:
        return False

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :

        if element.tag == "way":
          node_refs = []
          for nd in element.iter("nd"):
              node_refs.append(nd.attrib["ref"])
          if len(node_refs) > 0:
              node["node_refs"] = node_refs
          
        if "id" in element.attrib:
          node["id"] = element.attrib["id"]

        node["type"] = element.tag

        if "visible" in element.attrib:
          node["visible"] = element.attrib["visible"]

        created = {}
        for tag in CREATED:
          if tag in element.attrib:
            created[tag] = element.attrib[tag]
        if len(created) > 0:
          node["created"] = created

        pos = []    
        if "lat" in element.attrib and "lon" in element.attrib:
          lat = element.attrib["lat"]
          lon = element.attrib["lon"]
          if isfloat(lat) and isfloat(lon):
            pos = [float(lat), float(lon)]
            node["pos"] = pos
 
        address = {}
        for tag in element.iter("tag"):
          split_k = tag.attrib['k'].split(":")
          if len(split_k) == 1:
            node[split_k[0]] = tag.attrib['v']
          elif len(split_k) == 2:
            address[split_k[1]] = tag.attrib['v']

        if len(address) > 0:
          node["address"] = address
          
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('example.osm', True)
    #pprint.pprint(data)
    
    correct_first_elem = {
        "id": "261114295", 
        "visible": "true", 
        "type": "node", 
        "pos": [41.9730791, -87.6866303], 
        "created": {
            "changeset": "11129782", 
            "user": "bbmiller", 
            "version": "7", 
            "uid": "451048", 
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()


<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="CGImap 0.0.2">
 <bounds minlat="54.0889580" minlon="12.2487570" maxlat="54.0913900" maxlon="12.2524800"/>
 <node id="298884269" lat="54.0901746" lon="12.2482632" user="SvenHRO" uid="46882" visible="true" version="1" changeset="676636" timestamp="2008-09-21T21:37:45Z"/>
 <node id="261728686" lat="54.0906309" lon="12.2441924" user="PikoWinter" uid="36744" visible="true" version="1" changeset="323878" timestamp="2008-05-03T13:39:23Z"/>
 <node id="1831881213" version="1" changeset="12370172" lat="54.0900666" lon="12.2539381" user="lafkor" uid="75625" visible="true" timestamp="2012-07-20T09:43:19Z">
  <tag k="name" v="Neu Broderstorf"/>
  <tag k="traffic_sign" v="city_limit"/>
 </node>
 ...
 <node id="298884272" lat="54.0901447" lon="12.2516513" user="SvenHRO" uid="46882" visible="true" version="1" changeset="676636" timestamp="2008-09-21T21:37:45Z"/>
 <way id="26659127" user="Masch" uid="55988" visible="true" version="5" changeset="4142606" timestamp="2010-03-16T11:47:08Z">
  <nd ref="292403538"/>
  <nd ref="298884289"/>
  ...
  <nd ref="261728686"/>
  <tag k="highway" v="unclassified"/>
  <tag k="name" v="Pastower Straße"/>
 </way>
 <relation id="56688" user="kmvar" uid="56190" visible="true" version="28" changeset="6947637" timestamp="2011-01-12T14:23:49Z">
  <member type="node" ref="294942404" role=""/>
  ...
  <member type="node" ref="364933006" role=""/>
  <member type="way" ref="4579143" role=""/>
  ...
  <member type="node" ref="249673494" role=""/>
  <tag k="name" v="Küstenbus Linie 123"/>
  <tag k="network" v="VVW"/>
  <tag k="operator" v="Regionalverkehr Küste"/>
  <tag k="ref" v="123"/>
  <tag k="route" v="bus"/>
  <tag k="type" v="route"/>
 </relation>
 ...
</osm>

{'address': {'building_id': '366409',
            'city': 'Chicago',
            'country': 'US',
            'housename': 'Village Hall',
            'housenumber': '1412',
            'levels': '1',
            'postcode': '60067',
            'state': 'Illinois',
            'street': 'West Lexington St.'},
 'amenity': 'townhall',
 'building': 'yes',
 'created': {'version': '0.6'},
 'cuisine': 'sausage',
 'highway': 'service',
 'id': '1557627',
 'name': 'Village Hall',
 'node_refs': ['2199822281',
              '2199822390',
              '2199822392',
              '2199822369',
              '2199822370',
              '2199822284',
              '2199822281'],
 'outdoor_seating': 'no',
 'phone': '(773)-654-1347',
 'pos': [42.1251718, -88.0780576],
 'restriction': 'only_right_turn',
 'shop': 'doityourself',
 'smoking': 'no',
 'source': 'GPS',
 'takeaway': 'yes',
 'type': 'restriction',
 'visible': 'true'}


[{u'_id': u'502142', u'count': 81237},
 {u'_id': u'10786', u'count': 48595},
 {u'_id': u'451693', u'count': 36029},
 {u'_id': u'7168', u'count': 20581},
 {u'_id': u'4732', u'count': 19649},
 {u'_id': u'38487', u'count': 18254},
 {u'_id': u'91568', u'count': 10597},
 {u'_id': u'16591', u'count': 10431},
 {u'_id': u'1746371', u'count': 9709},
 {u'_id': u'933061', u'count': 9098}]

 [{u'_id': None, u'count': 71210}]


[{u'_id': u'28145', u'count': 37},
 {u'_id': u'4732', u'count': 19},
 {u'_id': u'10786', u'count': 17},
 {u'_id': u'700119', u'count': 8},
 {u'_id': u'2809783', u'count': 2},
 {u'_id': u'1741793', u'count': 2},
 {u'_id': u'722137', u'count': 2}]