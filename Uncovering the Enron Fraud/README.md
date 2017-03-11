
# Uncovering the Enron Fraud

Enron was an American energy giant. At it's peak, Enron was worth more than $70 billion. Enron's might came crashing down in the wake of one of the biggest [corporate scandals](http://www.npr.org/news/specials/enron/) in 2001. This project aims at uncovering the perpatrators and parties to the fraud.

I look at a dataset composed of emails and financial information pertaining to 145 Enron insiders. It is my objective to use Supervised Machine Learning Classifiers to train an algorithm that correctly identifies Persons of Interest in the fraud.


## Dataset Exploration

The dataset in question is composed of **21** features for **146** people associated with Enron. Out of the 146, **18** executives are listed as Persons-of-Interest (PoIs). Clearly there is an imbalance in the number of PoIs vs the number of non-PoIs, this means an alogrithm is very likely to get the non-PoIs classified correctly. It will be prudent to implement rigorous validation, and the right evaluation metrics as a check for this imbalance.

To make a decision about what features to include in my analysis, I'd like to get a sense of how much information is contained in each. The following code should help me get an idea (I later converted the returned values into a Data Frame):

```python
c = defaultdict(int)

for i in enron_data.keys():
    for j in enron_data[i].keys():
        if enron_data[i][j] == 'NaN':
            c[j] += 1

c = dict(c)
c_sorted = sorted(c.items(), key = lambda x:x[1], reverse = True)
```


I can see the dataset is riddled with missing values. 20 out of the 21 features have atleast 20 missing values, the only feature that we have all information for is whether or not the person in question is a PoI.


```python
                     Features  Count    Percent
0               loan_advances    142  97.260274
1               director_fees    129  88.356164
2   restricted_stock_deferred    128  87.671233
3           deferral_payments    107  73.287671
4             deferred_income     97  66.438356
5         long_term_incentive     80  54.794521
6                       bonus     64  43.835616
7                 to_messages     60  41.095890
8     from_this_person_to_poi     60  41.095890
9     from_poi_to_this_person     60  41.095890
10    shared_receipt_with_poi     60  41.095890
11              from_messages     60  41.095890
12                      other     53  36.301370
13                   expenses     51  34.931507
14                     salary     51  34.931507
15    exercised_stock_options     44  30.136986
16           restricted_stock     36  24.657534
17              email_address     35  23.972603
18             total_payments     21  14.383562
19          total_stock_value     20  13.698630
```

I will exlude features with very high proportion of missing values (more than 50%) from my analysis.

Next, I think it will bode well to explore and look at missing values by person using the following code:

```python
d = defaultdict(int)

for i in enron_data.keys():
    for j in enron_data[i].keys():
        if enron_data[i][j] == 'NaN':
            d[i] += 1

d_sorted = sorted(c.items(), key = lambda x:x[1], reverse = True)
```

I will take a look at the top 20 people with the most missing values.


```python
                              Name                    Count  Percentage
0                LOCKHART EUGENE E                       20    0.952381
1                   WHALEY DAVID A                       18    0.857143
2                     WROBEL BRUCE                       18    0.857143
3    THE TRAVEL AGENCY IN THE PARK                       18    0.857143
4                    GRAMM WENDY L                       18    0.857143
5                    WODRASKA JOHN                       17    0.809524
6                  CLINE KENNETH W                       17    0.809524
7                     WAKEHAM JOHN                       17    0.809524
8                SCRIMSHAW MATTHEW                       17    0.809524
9                      GILLIS JOHN                       17    0.809524
10                    SAVAGE FRANK                       17    0.809524
11                 LOWRY CHARLES P                       16    0.761905
12                     CHAN RONNIE                       16    0.761905
13                 URQUHART JOHN A                       16    0.761905
14                 MENDELSOHN JOHN                       16    0.761905
15                  MEYER JEROME J                       16    0.761905
16              GATHMANN WILLIAM D                       16    0.761905
17         PEREIRA PAULO V. FERRAZ                       16    0.761905
18              BLAKE JR. NORMAN P                       16    0.761905
19          CHRISTODOULOU DIOMEDES                       16    0.761905
```


Right away, I see some problem areas:

* `LOCKHART EUGENE E` has no information associated whatsoever.
* `THE TRAVEL AGENCY IN THE PARK` is not an actual person.

On [digging](http://www.travelweekly.com/Travel-News/Travel-Agent-Issues/Texas-agency-takes-a-huge-hit-from-Enron-s-fall) a little, I found that `THE TRAVEL AGENCY IN THE PARK` (TAP) was Enron's lead travel agent that was later rebranded as Alliance Worldwide. Sharon Lay held a 50% stake in TAP, and the Enron-TAP relationship was mired in accusations of favouritism.

### Outlier

I visualized `salary` vs `bonus` in a scatter plot, and found that one record, `TOTAL` was an outlier. This record represents the aggregate values of all the records in the dataset, and hence must be removed from analysis.


## Feature Selection

Feature Selection is crucial to training an accurate and efficient classifier. My dataset cosists of Fiancial + Email information. All variables measure either one of these two broad latent variables - financial incentives and email interaction with Persons of Interest. Intuitively, both these variables should have some special information associated with them.

I will check for the power of each of these features to test my hypothesis, and will try to include at least one feature measuring each of the two latent variables.

Apart from the features already included, I engineered two new features:

* `fraction_to_from_poi`: Represents the fraction - out of the total mails - that were sent to or received from persons of interest. This features represents how much any given person interacts with a person of interest.

* `wealth`: Represents the sum total of the Salary, Bonus, Total Stock Value, and Exercised Stock Options.

I then used `SelectKBest` to find the best features. I first chose 5 features, but I decided to add in test if adding more features betters precision and recall (It did.) I ended up choosing all features with a score more than 5, which left me with 8 features. I have listed them here:

```python
                   feature      score
0  exercised_stock_options  24.815080
1        total_stock_value  24.182899
2                    bonus  20.792252
3                   salary  18.289684
4                   wealth  15.369277
5          deferred_income  11.458477
6           total_payments   8.772778
7  shared_receipt_with_poi   8.589421
```

## The Algorithm

I tried out four algorithms with default parameters for starters. I split the dataset into train and test with a random seed of `41`. Here's how these algorithms performed: 

### Gaussian Naive Bayes Classifier

```python
Accuracy: 0.8787

Recall: 0.2

Precision: 1.0
```


### K Nearest Neighbors

```python
Accuracy: 0.8787

Recall: 0.2

Precision: 1.0
```


### Decision Tree Classifier

```python
Accuracy: 0.8787

Recall: 0.4

Precision: 0.6667
```


### AdaBoost

```python
Accuracy: 0.8787

Recall: 0.2

Precision: 1.0
```

### Random Forest

```python
Accuracy: 0.9091

Recall: 0.4

Precision: 1.0
```

The more than 80% accuracy is to be expected. As most of the dataset is composed of non-poi's, the classifiers do a good job of identifying the non-poi's. (I tried different splits, and the accuracy of any given algorithm still fell in the 75% - 85% range - Accuracy, in this case, is a misleading metric.)

The perfect precision scores are due to a lucky split (I verfied this, by running the algorithms on other splits by varying the random seeds). I will not bet my life on these scores.

I will focus on bettering three classifiers that had the best precision and recall scores - The Naive Bayes Classifier, K Nearest Neighbors and the Random Forest Classifier. (I should be selecting Ada Boost as well, but the performance of the classifier varied vastly based on the split.)


## Algorithm (Parameter) Tuning

It is imperative that we tune our algorithms to our data and available features to get the best possible performance. Tuning an algorithm lets us avoid overfitting, and ensure that the algorithm generalizes well. 

I selected the best combination of algorithm parameters using `GridSearchCV`. Grid Search lets me simultaneously validate my findings. 

### Feature Scaling

A properly scaled feature ensures efficiency and accuracy. I used `scikit-learn`'s `StandardScaler` to scale all my features to a standard form with zero mean, and unit variance. Of my algorithms, it is imperative that I feed the `KMeansClassifier` scaled features, and I have done so.


These are the new performances logged by my algorithms:

Best Score is the cross validated `f-1` score returned by `GridSearchCV`. The `f-1` score is the harmonic mean 

I calculated `recall` and `precision` on a separately created test set. 

```python
Gaussian Naive Bayes:

Best score: 0.315

Recall: 0.5
Precision: 0.333
```

```python
K-Nearest Neighbors

Best score: 0.311

Recall: 1.0
Precision: 1.0
```

```python
Random Forest

Best score: 0.328

Recall: 1.0
Precision: 1.0
```

I tried including two features I engineered `fraction_to_poi` and `fractio_from_poi` in the Naive Bayes Classifier, to check if I get an enhanced performance.

```python
Naive Bayes 

Recall: 0.3889
Precision: 0.4375
```
Including these leads to an increased precision score, but a reduced recall score - a tradeoff that is not acceptable to me.

## Validation

Validation is a key step to measure and ensure our algorithm generalizes well beyond the data we have. It is prudent to validate the veracity of the results the algorithm generates from the current dataset.

I implemented `StatifiedShuffleSplit` by means of `GridSearchCV`.

`GridSearchCV` tests classifiers by using cross-validation internally. It sets up a parameter grid with all possible combinations of specified parameter values, and recursively testing all of them. The best combination or set of parameter values is determined by examining the scores - `f-1` score in this case - returned by the classifier.

`StratifiedShuffleSplit` splits the dataset while making sure the split of the labels is balanced between testing and training sets. It is apt to use this as the method of cross-validation here because our dataset is mainly composed of non-PoIs, and regular `Kfold` cross-validation may split the data such that the training set does not contain any of the PoIs.


## Evaluation

For evaluating my classifiers, I used `recall` and `precision`. 

`recall`: Recall tells me of all the records marked as PoIs, how many were correctly classified as so by the classifier.

`precision`: Precision tells me of all the records classified as PoIs by the classifier, how many were actually PoIs.

Since I want to devise a sizeable web to identify people involved in the fraud - and mark them "Presons of Interest" (Not outright "guilty") - I am willing to compromise on `precision`, but not `recall`. In the case of a tradeoff, I will prefer high `recall` over `precision`. Overall, I would like robust scores on both ends.

Like all other metrics in `scikit-learn`, the higher the values for `precision` and `recall`, the better. 

I see that classifiers, Random Forest and K-Nearest Neighbors logged perfect precision and recall, but on testing the performance with `tester.py`, I see that their performance dropped sizeably.

```python
Random Forest

Recall: 0.54955
Precision: 0.27450
```

```python
K-Nearest Neighbors

Recall: 0.47544
Precision: 0.24200
```
I can see that my classifiers did not generalize as well as I had hoped or liked. Though, they excedeed the threshold of 0.3 for Precision, they fell short on the crucial Recall. The performance of these algorithms can be improved, but at significant computing cost. 

This cost is not something I am willing to bear at the moment, because my Naive Bayes Classifier qualifies the threshold.

```python
Gaussian Naive Bayes

Recall: 0.36479
Precision: 0.31700
```
