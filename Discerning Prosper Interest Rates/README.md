# Discerning Prosper Interest Rates 
### Abhishek Anirudhan
========================================================

This project explores a dataset of loans generated by the peer-to-peer lending service Prosper between 2006 and 2014. The dataset contains over 100,000 observations described over 81 features.I took up this project with the intention of probing the dataset to discern any interesting patterns and explain them.

I went through the variable descriptions, and started plotting to get a sense of the borrower's profile and characteristics of the loans. The plot for borrowers rate caught my eye. I saw that each borrower got a custom rate, and proceeded to understand what determines the rate offered.

On visiting the Prosper [website](https://www.prosper.com/borrower/#/prospect/registration) I found that Prosper promts you to enter information regarding the required Loan Amount, Employment Status, Purpose of the Loan and Income. I then went on to explore these variables and a few others.

While I got an approximate of what could be driving the borrower rate in some instances (like Unemployed and Non-homeowners get offered higher rates on average), I was mostly stuck with weak relationships between the borrower rate and other variables. I hypothesized that the weak relationship was on account that any standalone variable could not explain the Borrower Rate, but maybe a combination of variables could - however, this looked unlikely given the bivariate plots.

As expected, the linear model came with an R-squared value of 0.3. At this point, I decided to take a look at other variables that might explain the borrower rate better. I found these variables to be the Prosper Score, Credit Score and the time. The final model could explain 70% of the variance. However it's limitations are that it was based on a dataset riddled with missing values, leading to loss in accuracy. The model is not a robust predictive model.