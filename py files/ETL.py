import settings #configure own keyword to stream 
import TwitterKeys #Library containing twitter keys and tokens 
import dictionary #get states dictionary
import awsDB #parameters to connect to SQL database
import stopwords #personal stop words

from tweepy.streaming import StreamListener #listening to tweets
from tweepy import OAuthHandler #get verification
from tweepy import Stream #data is coming from

import re #library to use regular expression for cleaning text
from autocorrect import Speller #corrects mispelt words
import nltk #library to get part of speech
from nltk import word_tokenize #library to tokenize a string
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob #library to get text sentiment

import pandas as pd #library to convert string to datetime
import mysql.connector #connect to mySQL

#customize StreamListener class
class myStreamListener(StreamListener):
        
    def uniform(self):
    # change state values to only contain full state name
        for abbr,name in dictionary.states.items():
            if (abbr in self.location) | (name in self.location):
                abbr_code = abbr
                full_name = name
        
        return abbr_code, full_name
    
    def clean_text(self):
    #change all the letters in the text to lowercase
        text = self.tweet.lower()
    
        '''The next block of codes uses
        regular expressions to find certain
        string patterns and modifies them.'''
    
        text = re.sub(r"\n", "", text)
        text = re.sub("[^\x00-\x7F]+", "", text)
        text = re.sub("@[\w]*", "", text)
        text = re.sub("#[\S]*", "", text)
        text = re.sub("http[\S]+", "", text)
        text = re.sub("[\S]*\d[\S]*", " ", text)
        text = re.sub("[^\w\s]", " ", text)
        text = re.sub(r"(\w)\1{2,}", r"\1\1", text) 
    
        '''The for loop below takes all
        contracted words in the text and
        replaces them with the non-contracted
        version'''
        
        for key,val in dictionary.transform.items() :
            if key in text :
                text = re.sub("^"+key+"[\s]+", val+" ", text)
                text = re.sub("[\s]+"+key+"[\s]+", " "+val+" ", text)
        
        #fixes spelling errors
        spell = Speller()
        text = spell(text)
        
        #tokenizes each text
        word_list1 = word_tokenize(text)
    
        clean_verb = ''
        clean_text = ''
        final_text = ''
        wnl = WordNetLemmatizer()
        
        for word in word_list1 :
            #removes the inflection endings for verbs
            clean_verb += wnl.lemmatize(word,pos = 'v') + ' '
        
        word_list2 = word_tokenize(clean_verb)
        
        for word in word_list2 :
            #removes the inflection endings for nouns
            clean_text += wnl.lemmatize(word,pos = 'n') + ' '
        
        word_list3 = word_tokenize(clean_text)
        
        #ignores stopwords in tweet
        imp_words = [word for word in word_list3 if word not in stopwords.STOPWORDS]
        
        for word in imp_words:
            final_text += word + ' '
        
        return final_text
    
    def insertData(self):
        #load transformed data into AWS database
        sql_query = '''INSERT INTO {} 
                       (creation, state_code, state_name, clean_tweet, adjective, polarity, category)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)'''.format(awsDB.table)
        
        parameters = (
            self.creation, 
            self.state_code, 
            self.state_name,
            self.clean_tweet, 
            self.adjective,
            self.polarity,
            self.category
        )
        
        cur.execute(sql_query, parameters)
        conn.commit()
    
    # Extraction - data is collected in the "on_data" method of class StreamListener
    
    def on_status(self, status):
        #Transformation
        if (status.text.startswith('RT')) | (status.retweeted == True):
            # ignore if retweet
            return True
        
        if status.user.location == None:
            # ignore is there is no location
            return True
        
        if (
            (any(abbr in status.user.location for abbr in dictionary.states.keys())) |
            (any(name in status.user.location for name in dictionary.states.values()))
        ):
            #assign location's text to a variable if state 
            #abbreviation or state name is in location's text
            self.location = status.user.location
        else:
            #ignore if state abbreviation or state name is not in location's text
            return True
            
        #assign the date and time the tweet was posted to a variable
        creation = status.created_at
        creation = pd.to_datetime(creation)
        
        if status.truncated:
            #get full text if tweet is truncated
            self.tweet = status.extended_tweet['full_text']
        else:
            self.tweet = status.text
    
        self.creation = creation.strftime('%Y-%m-%d %H:%M')
        self.state_code, self.state_name = self.uniform()
        self.clean_tweet = self.clean_text()
        
        s = ''
        list_of_words = word_tokenize(self.clean_tweet)
        for tup in nltk.pos_tag(list_of_words):
            if tup[1] == 'JJ':
                s += tup[0] + ' '
        
        self.adjective = s
            
        
        self.polarity = TextBlob(self.clean_tweet).sentiment.polarity 
        
        if self.polarity == 0:
            self.category = 0
        elif self.polarity > 0:
            self.category = 1
        else:
            self.category = -1
        
        #Load
        self.insertData()  
        
    def on_error(self, status_code):
        if status_code == 420:
            #return false will disconnect the stream after limit is reached
            return False

if __name__ == '__main__':
    #connect to sql database
    conn = mysql.connector.connect(
        user = awsDB.user,
        password = awsDB.password,
        database = awsDB.db,
        host = awsDB.host, 
        port = awsDB.port
    )

    #create desired table if table does not exist
    table_query = '''CREATE TABLE IF NOT EXISTS {} (
                     creation text NOT NULL,
                     state_code text NOT NULL,
                     state_name text NOT NULL,
                     clean_tweet text NOT NULL,
                     adjective text NOT NULL,
                     polarity FLOAT NOT NULL,
                     category FLOAT NOT NULL
                     );'''.format(awsDB.table)

    #create table and commit changes
    cur = conn.cursor()
    cur.execute(table_query)
    conn.commit()

    # Connect to Twitter Streaming API and stream data
    listener = myStreamListener()
    au = OAuthHandler(TwitterKeys.CONSUMER_KEY, TwitterKeys.CONSUMER_SECRET)
    au.set_access_token(TwitterKeys.ACCESS_TOKEN, TwitterKeys.ACCESS_TOKEN_SECRET)
    stream = Stream(au,listener)
    stream.filter(track=[settings.KEYWORD], languages=['en'])

    #close connection to SQL database
    cur.close()
    conn.close()
    #close connection with Twitter Streaming API
    stream.disconnect()