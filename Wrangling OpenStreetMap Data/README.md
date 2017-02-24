
# Wrangling Openstreetmap Data with SQL
---

**Location:** Hyderabad, India

* [OpenStreetMap](https://www.openstreetmap.org/search?query=Hyderabad#map=10/17.4050/78.5275)
* [Dataset](https://mapzen.com/data/metro-extracts/metro/hyderabad_india/)


I chose to examine the map area for the city of Hyderabad because it's my city of residence. I thought I could leverage local knowledge to efficiently explore the dataset, spot inconsistencies and hopefully, as a further step, enrich the Hyderabad OpenStreetMap community. 


## Top-Level Audit
---

I used the ```parse.py``` to get a top level overview of my XML file. I saw that the dataset was composed of the following tags:

* ```'node' : 3224658```
* ```'relation' : 2330```
* ```'way' : 769154```
* ```'member' : 9668```
* ```'tag' : 858681```
* ```'nd' : 4075156```


## Problems Encountered
---

On auditing a sample of the dataset using `audit.py`, I ran into the following errors:

* Incorrect Postal Code: *`996544`*

* Inconsistent City Names: *`HYDERABAD, Hyderabad, hyderabad`*

* Flouting of Convention (In filling the addresses): *`Plot 103-105, KPBH 5th Phase`*

I will proceed to correct for these errors.


### Flouting of Naming Convention

The biggest problem I encountered was an open flouting of naming convention while filling the data. I raised a clarification [here](https://help.openstreetmap.org/questions/54753/osm-data-inconsistency-hyderabad). The full address was filled in the `addr:street` key instead of the `addr:full` key. I will work on a `sample.py` of the dataset to look and correct for these errors.

On taking a closer look I see that my sample has: 

* `70` `addr:street` keys, and no `addr:full` keys.

I will correct for this by changing the `addr:street` key for values that have a comma separated value (indicating an address contaning details more than the street name. This addresses only a small part of the inconsistencies the street address part of the dataset is riddled with.

```xml
<tag k="addr:street" v="Opp to Sai baba temple, Gudimalkapur crossroads, Mehedipatmam" />
```

to `addr:full` key.

```xml
<tag k="addr:full" v="Opp to Sai baba temple, Gudimalkapur crossroads, Mehedipatmam" />
```

I achieved this using the following code:

```python
def clean_up(osm_file):
     for element in get_element(osm_file):
         for tag in element.iter("tag"):
             if street_name(tag):
                 if ',' in tag.attrib['v']:
                     k = tag.attrib['k'].split(':', 1)
                     k[1] = 'full'
                     tag.attrib['k'] = ':'.join(k)
```


### Inconsistency in City Name

I found that the `addr:city` key contained two types of errors:

* Name of suburbs instead of the city name: `'Nizampet'`, `'Ramanthapur'`

* Inconsistency in the case: `'HYDERABAD'`,`'hyderabad'`

I will convert all of these into the format `'Hyderabad'` using the following function:

```python
def clean_up(osm_file):
    for element in get_element(osm_file):
        for tag in element.iter("tag"):
                    .
                    .
                    .
            if city_name(tag):
                if tag.attrib['v'] != "Hyderabad":
                    tag.attrib['v'] = "Hyderabad"
                    print tag.attrib['v']
```


### Incorrect Postal Code

Hyderabad has 6 digit postal codes in the form 500 xxx, 501 xxx and 502 xxx.

I found only a few instances of incorrect postal codes: 

* A postal code with incorrect number of digits: `'5021377'`
* An out of bounds postal code with correct number of digits: `'996544'`
* Incorrectly spaced postal code: `'500 081'`

I found only one instance of a postal code with the right number of digits, but out of bound. I found several instances where the postal codes were more or less than 6 digits. I will default these values to `'500001'`, and correct for other errors using the following code:

```python
def clean_up(osm_file):
    for element in get_element(osm_file):
        for tag in element.iter("tag"):
                    .
                    .
                    .
            if is_postal_code(tag):
                if tag.attrib['v'] in ['500 032','500 081']:
                    k = tag.attrib['v'].split(' ', 1)
                    tag.attrib['v'] = ''.join(k)
                    print tag.attrib['v']
                
                if tag.attrib['v'] == '996544':
                    tag.attrib['v'] = '500001'
                    print tag.attrib['v']
                    
                if len(tag.attrib['v']) != 6:
                    tag.attrib['v'] = '500001'
                    print tag.attrib['v'] 
```

The corrected postal codes should look like this:

* A seven digit postal code: `'50001'`
* An out of bounds postal code: `'500001'`
* Incorrectly spaced postal code: `'500081'`


## Dataset Overview and Exploration
---

Here I included some basic statistics about my database, the code used to create and fill in the tables in my database, and some additional exploration that I carried out.


### File Sizes

```
hyderabad.osm ...... 714 MB
hyderabad.db ....... 475 MB
nodes.csv .......... 268 MB
node_tags.csv ...... 0.76 MB
way.csv ............ 47 MB
way_tags.csv ....... 99.6 MB
way_nodes.csv ...... 28 MB

```

I used sqlite3 to create and query my database.


### Creating the Database

```sql
sqlite3 hyderabad.db
```

I created the tables by defining each tables schema.

### Creating Tables
```sql
CREATE TABLE nodes(
id INT PRIMARY KEY,
lat FLOAT,
lon FLOAT,
user STRING,
uid INT,
version STRING,
changeset INT,
timestamp STRING
);

CREATE TABLE node_tags(
id INT REFERENCES nodes(id),
key STRING,
value STRING,
type STRING
);

CREATE TABLE way(
id INT PRIMARY KEY,
user STRING,
uid INT,
version STRING,
changeset INT,
timestamp STRING
);

CREATE TABLE way_nodes(
id INT REFERENCES way(id),
node_id INT,
position INT
);

CREATE TABLE way_tags(
id INT REFERENCES way(id),
key STRING,
value STRING,
type STRING
);
```

I imported data into the database from  `csv` files.


### Importing Data

```sql
.mode csv

.import nodes.csv nodes
.import nodes_tags.csv node_tags
.import ways.csv way
.import ways_nodes.csv way_nodes
.import ways_tags.csv way_tags
```

Now that the database is defined, we can query it to get some basic statistics.


### Number of Nodes
```sql
SELECT COUNT(*) FROM nodes;
```
> 3224659



### Number of Ways
```sql
SELECT COUNT(*) FROM way;
```
> 769155



### Number of Unique Users
```sql
SELECT COUNT(DISTINCT(temp.uid))          
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) temp;
```
> 912



### Top Contibutors 
```sql
SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM way) e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10;
```

```
> himabindhu: 145203
> saikumar: 132510
> bindhu: 129441
> anushapyata: 122079
> venkatkotha: 121777
> Apreethi: 119837
> harisha: 110980
> masthanvali: 107318
> udaykanth: 90380
```



### Top Amenities
```sql
SELECT value, COUNT(*) as num
FROM node_tags
WHERE key='amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```

```
> place_of_worship: 243
> restaurant: 233
> atm: 230
> bank: 217
> fuel: 140
> hospital: 109
> school: 106
> pharmacy: 97
> cafe: 90
> fast_food: 84
```



### Most Popular Religion
```sql
SELECT node_tags.value, COUNT(*) as num
FROM node_tags 
    JOIN (SELECT DISTINCT(id) FROM node_tags WHERE value='place_of_worship') i
    ON node_tags.id=i.id
WHERE node_tags.key='religion'
GROUP BY node_tags.value
ORDER BY num DESC
LIMIT 1;
```

```
> hindu: 102
```



### City Constitution
```sql
SELECT value, COUNT(*) as num
FROM node_tags
WHERE key='place'
GROUP BY value
ORDER BY num DESC
LIMIT 5;
```
```
> neighbourhood: 1086
> suburb: 177
> village: 47
> locality: 41
> town: 6
```



### Popular Cuisines
```sql
SELECT node_tags.value, COUNT(*) as num
FROM node_tags 
    JOIN (SELECT DISTINCT(id) FROM node_tags WHERE value='restaurant') i
    ON node_tags.id=i.id
WHERE node_tags.key='cuisine'
GROUP BY node_tags.value
ORDER BY num DESC
LIMIT 5;
```

```
> indian: 35
> regional: 12
> vegetarian: 8
> chinese: 6
> coffee_shop: 6
```

## Additional Ideas and Conclusion

As documented above, the biggest concern here was the flouting of conventions. While the more experienced users did adhere to the rules laid out in the wiki, most others did not. Given that Openstreetmap is open source, collaborative and is based on Volunteered Geographic Information, it wouldn't be fair of me to recommend solutions that will prove to be expensive.

Keeping that in mind, a big chunk of errors will be eliminated before if users are made aware of rules for filling in keys before they start typing - in the form of a tool tip or a pop-up cloud perhaps. Though people might blow through these suggestion pop-ups any way, I think it will have a definite impact on reducing the error rate. 


I was really encouraged to see the participation and size of the Hyderabad city map. Though the detail still does not meet with tools like Google Maps, it is not very bad either. In this collaborative age, contribution and participation should only grow.


