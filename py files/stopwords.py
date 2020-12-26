'''Modify stop words'''

from nltk.corpus import stopwords #library to get english stop words

list_of_stopwords = ['''enter a list of stop words you wish to remove from tweets''']
STOPWORDS = set(stopwords.words('english') + list_of_stopwords)