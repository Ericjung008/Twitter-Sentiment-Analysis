# Twitter-Sentiment-Analysis

## Introduction
Due to the high volume of tweets posted everyday, Twitter is an excellent source to collect product reviews about Xbox. Since Twitter is a social media platform, the data will consist of many internet slang, incomplete information, and misinformation. Analyzing these type of data can lead to poor business decisions. However, after the raw data is properly handled, tweets can be represented in such a way to assist stakeholders into making insightful decisions and improve customer satisfaction.

## Objective
There are two objectives for this project:
1. Build an ETL pipeline
2. Create an interactive, real-time dashboard based on data collected from the ETL pipeline

## Metric 
A cost function was used as the evaluation metric for this project. The optimal threshold was chosen based on the highest savings.

## Approach
The following steps were taken to complete the project:
1. Import libraries and dataset
3. Exploratory Data Analysis
4. Feature Engineering
5. Feature Selection
6. Data Wrangling
7. Base Scores Model Evaluation
8. Hyperparameter Tuning
9. Model Selection
10. Cost Function

## Model Selection
Four models were trained through three methods:
1. No Sampling
2. Undersampling
3. Oversampling

The model was chosen based on the highest Average Precision score.

## Technologies
Application: Jupyter Notebook<br>
Programming Language: Python 3.7.4<br>
Libraries: Numpy, Pandas, Scipy, Matplotlib, Seaborn, Scikit-learn, XGBoost, Imblearn<br>

## Project Files
* [README](https://github.com/Ericjung008/Device-Failure/blob/master/README.md)
* [Project](https://github.com/Ericjung008/Device-Failure/blob/master/Device%20Failure%20Prediction.ipynb)
* [Dataset](https://github.com/Ericjung008/Device-Failure/blob/master/failures.csv)
