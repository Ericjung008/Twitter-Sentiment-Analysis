import awsDB #amazon web service keys
import settings #configure own keyword to stream data

import pandas as pd #library to work with dataframes
import datetime #library to access methods involving date & time

#visualization libraries
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import nltk #library to use natural language processing methods
from nltk import word_tokenize #library to tokenize a string
from sklearn.feature_extraction.text import CountVectorizer #creates a word count matrix

from sklearn.ensemble import RandomForestClassifier #Random Forest algorithm
from sklearn.metrics import accuracy_score #metric

import mysql.connector #connect to sql databse

import logging #library to prevent update/error message in terminal

#library to create dashboard
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


app = dash.Dash(__name__, external_stylesheets = [dbc.themes.CYBORG])

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

colors = {'background': 'black',
          'text': 'white'}

twitter = pd.read_csv('Twitter.csv')
train = twitter.dropna()

app.layout=html.Div(
    [ 
        html.Br(),
        
        html.H5(
            children='Twitter Sentiment Analysis on {}'.format(settings.KEYWORD.capitalize()),
            style = dict(color = colors['text'], paddingLeft = '30px')
        ),
        
        html.Br(),
        
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(
                                id = 'Line Plot',
                                config = {'displayModeBar': False}
                            ),
                            width = 6
                        ),
                        dbc.Col( 
                            html.Div(
                                children = [
                                    html.Br(),
                                    
                                    html.P(
                                        id = 'Amount',
                                        style = {
                                            'fontSize': 14,
                                            'fontWeight': 'bold',
                                            'color': colors['text'],
                                            'border': '5px rgba(47,79,79,0.8) double',                
                                            'height': '50px',
                                            'width': '75%',
                                            'marginTop': '15px',
                                            'marginLeft': '50px',
                                            'paddingTop': '10px',
                                            'textAlign': 'center'
                                        }
                                    ),
                                    
                                    html.P(
                                        id = 'Metric',
                                        style = {
                                            'fontSize': 14,
                                            'fontWeight': 'bold',
                                            'color': colors['text'],
                                            'border': '5px rgba(47,79,79,0.8) double',                
                                            'height': '50px',
                                            'width': '75%',
                                            'marginLeft': '50px',
                                            'paddingTop': '9px',
                                            'textAlign': 'center'
                                        }
                                    ),
                                ]
                            ),
                            width = 3
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id = 'Pie Chart',
                                config = {'displayModeBar': False}
                            ), 
                            width = 3
                        )
                    ]
                ),
                
                html.Br(),
                
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(
                                id = 'Choropleth Map',
                                config = {'displayModeBar': False}
                            ), 
                            width = 6
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id = 'Bar Graphs',
                                config = {'displayModeBar': False}
                            ),
                            width = 6
                        )                           
                    ]
                )
            ]
        ),
            
        dcc.Interval(
            id = 'interval-component-fast', 
            interval = 1*10000, #in milliseconds
            n_intervals = 0 #automatically incremented after interval time has passed
        ),
        
        dcc.Interval(
            id = 'interval-component-slow',
            interval = 1*604800000, # update every week
            n_intervals = 0
        )
    ],
)

@app.callback(
    Output(component_id = 'Line Plot', component_property = 'figure'),
   [Input(component_id = 'interval-component-fast', component_property = 'n_intervals')]
)

def update_line(n):
    
    sql_query = 'SELECT creation, category FROM {}'.format(settings.KEYWORD)

    conn = mysql.connector.connect(
        user = awsDB.user,
        password = awsDB.password,
        database = awsDB.db,
        host = awsDB.host, 
        port = awsDB.port
    )

    sentimentDF = pd.read_sql(sql = sql_query, con = conn, parse_dates = ['creation'])
    
    conn.close()
    
    x_start = datetime.datetime.utcnow() - datetime.timedelta(minutes = 30)
    timeDF = sentimentDF[sentimentDF['creation'] > x_start]
    x_range = pd.Series(timeDF['creation'].unique())
    
    grpDF = timeDF.groupby(['creation','category']).agg({'category':'count'})
    grpDF.rename(columns = {'category': 'totalCount'},inplace = True)
    grpDF.reset_index(inplace = True)
    
    pivotDF = grpDF.pivot(index = 'creation', columns = 'category', values = 'totalCount')
    pivotDF.fillna(0, inplace = True)
    
    neutral_Ser = pivotDF[0.0]
    negative_Ser = pivotDF[-1.0]
    positive_Ser = pivotDF[1.0]
    
    line = go.Figure()
    
    line.add_trace(
        go.Scatter(
            x = x_range,
            y = neutral_Ser,
            mode = 'lines',
            name = 'Neutral',
            marker = dict(color = 'rgb(0, 204, 180)')
        )
    )
    
    line.add_trace(
        go.Scatter(
            x = x_range,
            y = negative_Ser,
            mode = 'lines',
            name = 'Negative',
            marker = dict(color = 'rgb(255, 95, 59)')
        )
    )
    
    line.add_trace(
        go.Scatter(
            x = x_range,
            y = positive_Ser,
            mode = 'lines',
            name = 'Positive',
            marker = dict(color = 'rgb(79, 94, 255)')
        )
    )
            
    line.update_layout(
        showlegend = False,
        plot_bgcolor = 'rgba(0,0,0,0)',
        paper_bgcolor = 'rgba(0,0,0,0)',
        title_text = 'Tweets Collected Per Minute (UTC Timezone)',
        title_font_color = colors['text'],
        title_font_size = 11,
        margin_t = 20,
        margin_b = 0,
        margin_r = 0,
        margin_l = 45,
        height = 185,
        xaxis = dict(tickfont = dict(color = colors['text']), gridcolor = 'rgba(47,79,79,0.8)'),
        yaxis = dict(tickfont = dict(color = colors['text']), gridcolor = 'rgba(47,79,79,0.8)')
    )
        
    return line

@app.callback(
    Output(component_id = 'Amount', component_property = 'children'),
    [Input(component_id = 'interval-component-fast', component_property = 'n_intervals')]
)

def numData(n):
    
    sql_query = 'SELECT creation FROM {}'.format(settings.KEYWORD)
    
    conn = mysql.connector.connect(
        user = awsDB.user,
        password = awsDB.password,
        database = awsDB.db,
        host = awsDB.host, 
        port = awsDB.port
    )
    
    createdDF = pd.read_sql(sql = sql_query, con = conn)
    
    num_of_tweets = len(createdDF)
    numString = '{:.2f}K Tweets Collected'.format(num_of_tweets/1000)
    
    return numString
    
          
@app.callback(
    Output(component_id = 'Metric', component_property = 'children'),
    [Input(component_id = 'interval-component-slow', component_property = 'n_intervals')]
)
        
def accuracy(n):
    
    sql_query = 'SELECT clean_tweet, category FROM {}'.format(settings.KEYWORD)
    
    conn = mysql.connector.connect(
        user = awsDB.user,
        password = awsDB.password,
        database = awsDB.db,
        host = awsDB.host, 
        port = awsDB.port
    )
    
    ratingDF = pd.read_sql(sql = sql_query, con = conn)
    
    conn.close()
    
    if len(ratingDF) < 10000:
        metricDF = ratingDF.copy()
    else:
        metricDF = ratingDF[-10000:]
        
    vect = CountVectorizer()
    
    x_train_dtm = vect.fit_transform(train['clean_text'])
    x_test_dtm = vect.transform(metricDF['clean_tweet'])
    y_train = train['category']
    y_test = metricDF['category']
    
    rf = RandomForestClassifier()
    rf.fit(x_train_dtm, y_train)
    
    prediction = rf.predict(x_test_dtm)
    
    result = accuracy_score(prediction, y_test)
    metString = '{}% Categorizing Accuracy'.format(int(round(result*100)))
    
    return metString
                
@app.callback(
    Output(component_id = 'Pie Chart', component_property = 'figure'),
    [Input(component_id = 'interval-component-fast', component_property = 'n_intervals')]
)

def update_pie(n):
    
    sql_query = 'SELECT category FROM {}'.format(settings.KEYWORD)
    
    conn = mysql.connector.connect(
        user = awsDB.user,
        password = awsDB.password,
        database = awsDB.db,
        host = awsDB.host, 
        port = awsDB.port
    )
    
    catDF = pd.read_sql(sql = sql_query, con = conn)
    
    conn.close()
    
    labels = ['Neutral','Negative','Positive']
    
    totalNeutral = len(catDF[catDF['category'] == 0])
    totalNegative =  len(catDF[catDF['category'] == -1])
    totalPositive = len(catDF[catDF['category'] == 1])
    values = [totalNeutral, totalNegative, totalPositive]
    
    pie = go.Figure(
        go.Pie(
            labels = labels, 
            values = values, 
            hole = 0.65,
            customdata = values,
            hovertemplate = 'Number of tweets: %{customdata}<extra></extra>',
            marker = {
                'colors': ['rgb(0, 204, 180)','rgb(255, 95, 59)','rgb(79, 94, 255)'],
                'line' : dict(color=colors['text'], width = 1.5)
            }
        )
    )

    pie.update_layout(
        plot_bgcolor = 'rgba(0,0,0,0)',
        paper_bgcolor = 'rgba(0,0,0,0)',
        title_text = 'Sentiment Distribution',
        title_font_color = colors['text'],
        title_font_size = 11,
        title_x = 0.36,
        title_y = 0.99,
        height = 185,
        margin_b = 5,
        margin_t = 25,
        margin_l = 0,
        legend_x = 0.85,
        legend_y = 1.10,
        legend_font_color = colors['text']
    )
  
    return pie
        
    
@app.callback(
    Output(component_id = 'Choropleth Map', component_property = 'figure'),
    [Input(component_id = 'interval-component-fast', component_property = 'n_intervals')]
)

def update_choropleth(n):
    
    sql_query = 'SELECT state_code, state_name, polarity FROM {}'.format(settings.KEYWORD)

    conn = mysql.connector.connect(
        user = awsDB.user,
        password = awsDB.password,
        database = awsDB.db,
        host = awsDB.host, 
        port = awsDB.port
    )

    stateDF = pd.read_sql(sql = sql_query, con = conn)
    
    conn.close()

    avgDF = stateDF.groupby('state_code').agg({'state_name': 'first', 'polarity': 'mean'})
    avgDF.reset_index(inplace = True)
   
    choroMap = px.choropleth(
        data_frame = avgDF,
        locationmode = 'USA-states',
        locations = 'state_code',
        scope = 'usa',
        color = 'polarity',
        color_continuous_scale = ['#e6e7ff','#3b43ff'],
        custom_data = ['state_name','polarity']
    )
    
    choroMap.update_traces(
        marker_line_color = 'white',
        hovertemplate = '<br>'.join([
            'State: %{customdata[0]}',
            'Avg sentiment: %{customdata[1]:.4f}'
        ])
    )
            
    choroMap.update_layout(
        plot_bgcolor = 'rgba(0,0,0,0)',
        paper_bgcolor = 'rgba(0,0,0,0)',
        title_text = 'Average Sentiment by State',
        title_font_color = colors['text'],
        title_x = 0.06,
        title_y = 0.94,
        geo = dict(bgcolor = 'rgba(0,0,0,0)', lakecolor = 'dodgerblue'),
        height = 350,
        margin_t = 30,
        margin_b = 20,
        coloraxis_colorbar = {
            'title': 'Sentiment Scale',
            'title_font_color': colors['text'],
            'tickfont_color': colors['text'],
            'len' : 0.80,
            'thickness':  15,
            'x': 0.90
        }
    )
    
    return choroMap

@app.callback(
    Output(component_id = 'Bar Graphs', component_property = 'figure'),
    [Input(component_id = 'interval-component-fast', component_property = 'n_intervals')]
)

def update_bars(n):
    
    sql_query = 'SELECT category, adjective FROM {}'.format(settings.KEYWORD)

    conn = mysql.connector.connect(
        user = awsDB.user,
        password = awsDB.password,
        database = awsDB.db,
        host = awsDB.host, 
        port = awsDB.port
    )

    wordsDF = pd.read_sql(sql = sql_query, con = conn)
    
    conn.close()

    pos_words = wordsDF.loc[wordsDF['category'] == 1.0, 'adjective']
    pos_cv = CountVectorizer(max_features = 5)
    pos_vect = pos_cv.fit_transform(pos_words)
    pos_mat = pd.DataFrame(data = pos_vect.toarray(), columns = pos_cv.get_feature_names())
    
    pos_word_scores = {}
    for col in pos_mat:
        pos_col_sum = sum(pos_mat[col])
        pos_word_scores[col] = pos_col_sum
    
    order_pos_dict = dict(sorted(pos_word_scores.items(), key = lambda x: x[1], reverse = True))
    
    neg_words = wordsDF.loc[wordsDF['category'] == -1.0, 'adjective']
    neg_cv = CountVectorizer(max_features = 5)
    neg_vect = neg_cv.fit_transform(neg_words)
    neg_mat = pd.DataFrame(data = neg_vect.toarray(), columns = neg_cv.get_feature_names())
    
    neg_word_scores = {}
    for col in neg_mat:
        neg_col_sum = sum(neg_mat[col])
        neg_word_scores[col] = neg_col_sum
    
    order_neg_dict = dict(sorted(neg_word_scores.items(), key = lambda x: x[1]))
    
    
    bars = make_subplots(
        rows = 1, cols = 2, 
        subplot_titles = (
            'Common Words Associated with Positive Tweets',
            'Common Words Associated with Negative Tweets'
        )
    )
    
    bars.add_trace(
        go.Bar(
            x = list(order_pos_dict.keys()),
            y = list(order_pos_dict.values()),
            customdata = list(order_pos_dict.values()),
            hovertemplate = '%{customdata}<extra></extra>',
            marker = {
                'color' : 'rgb(79, 94, 255)',
                'line': dict(width = 1.5)
            }
        ),
        row = 1,
        col = 1
    )
    
    bars.add_trace(
        go.Bar(
            x = list(order_neg_dict.keys()),
            y = list(order_neg_dict.values()),
            customdata = list(order_neg_dict.values()),
            hovertemplate = '%{customdata}<extra></extra>',
            marker = {
                'color': 'rgb(255, 95, 59)',
                'line': dict(width = 1.5)
            }
        ),
        row = 1,
        col = 2
    )
    
    bars.update_layout(
        plot_bgcolor = 'rgba(0,0,0,0)',
        paper_bgcolor = 'rgba(0,0,0,0)',
        height = 350,
        margin_t = 40,
        margin_b = 55,
        margin_l = 30,
        showlegend = False,
        xaxis = dict(tickfont = dict(color = colors['text'], size = 10)),
        xaxis2 = dict(tickfont = dict(color = colors['text'], size = 10)),
        yaxis = dict(tickfont = dict(color = colors['text']), gridcolor = 'rgba(47,79,79,0.8)'),
        yaxis2 = dict(tickfont = dict(color = colors['text']), gridcolor = 'rgba(47,79,79,0.8)'),
        annotations = [
            {
                'font': {'size': 10, 'color': colors['text']},
                'y': 1.05
            },
            {
                'font': {'size': 10, 'color': colors['text']},
                'y': 1.05
            }
        ]
    )
     
    return bars           

if __name__ == '__main__':
    app.run_server(debug = False)