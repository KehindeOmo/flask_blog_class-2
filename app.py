import sqlite3
import csv
import requests
import pygal
from flask import Flask, render_template, request, url_for, flash, redirect, abort

API_KEY = '5JUJV1WUJIBMM95'

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'


with open('stocks.csv', 'r') as now:
    reader = csv.DictReader(now)
    stockSymbol = [row['Symbol'] for row in reader]

def getStockData(symbol, time_series_function):
    url = f"https://www.alphavantage.co/query?function={time_series_function}&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if 'Error Message' in data:
        print(f"Error: No data available for the stock symbol '{symbol}'")
        return None
    elif not data:
        print("Error: No data returned by the API.")
        return None
    
    time_series_key = list(data.keys())[1]  
    return data[time_series_key]


def plot_chart(chartType, data, title):

    # Create chart type
    if chartType == 1:
        chart = pygal.Bar()
    elif chartType == 2:
        chart = pygal.Line()
    else:
        print("Invalid chart type")
        return None
    
    # Extract data and set chart values
    dates = []
    values = []
    for date, daily_data in sorted(data.items()):
        dates.append(date)
        values.append(float(daily_data['4. close']))

    chart.title = title
    chart.x_labels = dates
    chart.add('Price', values)

    # Render chart to an svg
    return chart.render()

    # filter for plot

# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn


# use the app.route() decorator to create a Flask view function called index()
@app.route('/')
def index():
    return render_template('index.html', stockSymb=stockSymbol)

# route to create a post
@app.route('/stockData', methods =['POST'])
def stockData():
    symbol = request.form['symbol']
    time_series = request.form['timeSeries']
    chart_type = request.form.get('graph_type', '1')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    data = getStockData(symbol, time_series)
    if not data:
        return redirect(url_for('index'))
    
    filtered_data = filtered(data, start_date, end_date)

    svg_data = plot_chart(chart_type, filtered_data, f"{symbol} Stock Data from {start_date} to {end_date}")
    
    return render_template('index.html', stockSymb=stockSymbol, chart_svg=svg_data)


app.run(port=8000)