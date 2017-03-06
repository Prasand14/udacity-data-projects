#!/usr/bin/python

import sys
import pickle
from collections import defaultdict
import pandas as pd
from pprint import pprint
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest
from sklearn.cross_validation import train_test_split, StratifiedShuffleSplit
from sklearn.metrics import accuracy_score, recall_score, precision_score
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline



### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi'] # You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers

## Exploring the Dataset

c = defaultdict(int)
d = defaultdict(int)

for i in data_dict.keys():
    for j in data_dict[i].keys():
        if data_dict[i][j] == 'NaN':
            c[j] += 1
            d[i] += 1

c = dict(c)
d = dict(d)

c_sorted = sorted(c.items(), key = lambda x:x[1], reverse = True)
d_sorted = sorted(d.items(), key = lambda x:x[1], reverse = True)

# Deleting troubled records
del data_dict['LOCKHART EUGENE E']
del data_dict['THE TRAVEL AGENCY IN THE PARK']

## Checking for outliers

import matplotlib.pyplot as plt

for item in data_dict.values():
    plt.scatter(item['salary'], item['bonus'])
    
plt.show()

# Deleting troubled record
del data_dict['TOTAL']

for item in data_dict.values():
    plt.scatter(item['salary'], item['bonus'])

plt.show()

# Plotting fucntion to visaulize features
def plotter(data, x, y):
    X = []
    Y = []
    col = []
    
    for item in data_dict.values():
        X.append(item[x])
        Y.append(item[y])
        
    for i in data_dict.values():
        if i['poi']:
            col.append("red")
        else:
            col.append("blue")
    
    plt.scatter(x= X, y= Y, c = col)
 

### Task 3: Create new feature(s)

## Emails

features_emails = ["from_messages",
                   "to_messages",
                   "from_poi_to_this_person",
                   "from_this_person_to_poi"]

# New Features
for i in data_dict:
    item = data_dict[i]
    if all([item['from_poi_to_this_person'] != 'NaN',
            item['from_this_person_to_poi'] != 'NaN',
            item['to_messages'] != 'NaN',
            item['from_messages'] != 'NaN']):
        item["fraction_from_poi"] = float(item["from_poi_to_this_person"]) / float(item["from_messages"])
        item["fraction_to_poi"] = float(item["from_this_person_to_poi"]) / float(item["to_messages"])
    else:
        item["fraction_from_poi"] = 'NaN'
        item["fraction_to_poi"] = 'NaN'

        
        
## Financial

features_financial = ["salary",
                      "bonus",
                      "total_stock_value",
                      "exercised_stock_options"]

# New feature
for i in data_dict:
    item = data_dict[i]
    if all([item['salary'] != 'NaN',
            item['total_stock_value'] != 'NaN',
            item['exercised_stock_options'] != 'NaN',
            item['bonus'] != 'NaN']):
        item['wealth'] = sum([float(item[i]) for i in features_financial])
    else:
        item['wealth'] = 'NaN'
        

# Final Features list
        
features_list += ["bonus",
                  "salary",
                  "wealth",
                  "deferred_income",
                  "total_payments",
                  "total_stock_value",
                  "exercised_stock_options"]

features_list += ["fraction_from_poi",
                  "fraction_to_poi",
                  "shared_receipt_with_poi"]
                  

### Store to my_dataset for easy export below.
my_dataset = data_dict

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True, remove_NaN = True)
labels, features = targetFeatureSplit(data)

## Testing new features
new_labels_test, new_features_test = targetFeatureSplit(data)


#Select best features

selector = SelectKBest(k = 8)
selector.fit(features, labels)

best_features_list = zip(features_list[1:], selector.scores_)
best_features = sorted(dict(best_features_list).items(), key=lambda x: x[1], reverse=True)
best_features = pd.DataFrame(best_features[:8])

features_final = ["poi",
                  "exercised_stock_options",
                  "total_stock_value",
                  "bonus",
                  "salary",
                  "wealth",
                  "shared_receipt_with_poi"]

data = featureFormat(my_dataset, features_final, sort_keys = True, remove_NaN = True)
labels, features = targetFeatureSplit(data)


### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier



classifiers = [GaussianNB(),
               DecisionTreeClassifier(random_state = 50),
               AdaBoostClassifier(),
               RandomForestClassifier(),
               KNeighborsClassifier()]

classifier_names = ["Gaussian Naive Bayes",
                    "Decision Tree",
                    "Ada Boost",
                    "Random Forest",
                    "KNN"]

# Function to implement classifiers

def implement(classifier, features, labels):
    features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, random_state = 41)
    clf = classifier
    clf.fit(features_train, labels_train)
    pred = clf.predict(features_test)
    
    acc = accuracy_score(labels_test, pred)
    rec = recall_score(labels_test, pred)
    pre = precision_score(labels_test, pred)
    
    print "Accuracy: " + str(acc)
    print "Recall: " + str(rec)
    print "Precision: " + str(pre) 
    
    
for i in classifiers:
    clf = i
    print classifier_names[classifiers.index(i)]
    implement(clf, features, labels)
            

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html
# Example starting point. Try investigating other evaluation techniques!


# Splitting dataset for later testing  
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, random_state = 40)

# function to tune up performance:   
def tune_up(clf, parameters, features, labels):
    
    #Statified Shuffle Split to cross validate
    sss = StratifiedShuffleSplit(labels, 100, test_size=0.2, random_state=60)

    grid_search = GridSearchCV(clf, parameters, cv=sss, scoring='f1')
    grid_search.fit(features, labels)

    print "-----------------------------"
    print '\nBest score: %0.3f' % grid_search.best_score_
    
    print '\nBest Parameters: '
    best_parameters = grid_search.best_estimator_.get_params()
    pprint(best_parameters)
    
    clf = grid_search.best_estimator_
    return clf

# Function to test performance:    
def score_report(clf, features_test = features_test, labels_test = labels_test):
    pred = clf.predict(features_test)
    
    print "\nRecall: "
    print recall_score(labels_test, pred)
    
    print "\nPrecision: "
    print precision_score(labels_test, pred)
    print " "
        

# Gaussian Naive Bayes
pipeline = Pipeline(steps = [("normalizer", StandardScaler()),
                             ("gnb", GaussianNB())])

params = {}

clf_nb = tune_up(pipeline, params, features, labels)
score_report(clf_nb)

## Testing new feature

clf_nb_test = tune_up(pipeline, params, new_features_test, new_labels_test)
score_report(clf_nb_test, features_test = new_features_test, labels_test = new_labels_test)

# K-Nearest Neighbors

pipeline = Pipeline(steps = [("normalizer", StandardScaler()),
                             ("knn", KNeighborsClassifier())])

params = {"knn__n_neighbors" : [1, 5, 10, 15],
          "knn__weights" : ['uniform', 'distance'],
          "knn__leaf_size" : [5, 15, 30, 50],
          "knn__p" : [1, 2]}

clf_knn = tune_up(pipeline, params, features, labels)
score_report(clf_knn)

# Random Forest
pipeline = Pipeline(steps = [("normalizer", StandardScaler()),
                             ("rfc", RandomForestClassifier())])

params = {"rfc__n_estimators" : [5, 10, 15, 25],
          "rfc__criterion" : ["gini", "entropy"],
          "rfc__random_state" : [50]}

clf_rf = tune_up(pipeline, params, features, labels)
score_report(clf_rf)


clf = clf_nb
    
### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)