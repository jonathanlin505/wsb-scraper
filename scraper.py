"""
    This script has the following command-line uses:

        1. python ChihHsien_Lin_homework4.py
            this scrapes and prints out all three obtained datasets in full
        
        2. python ChihHsien_Lin_homework4.py --scrape
            this scrapes and prints out basic info of obtained datasets along with a sample of each dataset

        3. python ChihHsien_Lin_homework4.py --static filepath
            this skips all the scraping and accesses local csv datasets to print out basic info and dataset samples
            for this program, scraped datasets are stored as csv files in "datasets/" folder
            therefore, one would run the command-line like so: python ChihHsien_Lin_homework4.py --static datasets
"""

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
from datetime import datetime, timedelta
import argparse

# Argparse Section
parser = argparse.ArgumentParser()
parser.add_argument("--scrape", action = "store_true", help = "scrapes tickers from r/wallstreetbets and returns relevant stock and social media data")
parser.add_argument("--static", type = str, help = "obtains data stored in csv files")
args = parser.parse_args()

# If --static, skip web scraping, read-in local csv, and print results
if args.static:
    wsb_df = pd.read_csv(f'{args.static}/wsb_dataset.csv', index_col = 0)
    l30d_df = pd.read_csv(f'{args.static}/l30d_dataset.csv', index_col = 0)
    yahoo_df = pd.read_csv(f'{args.static}/yahoo_dataset.csv', index_col = 0)

    print("Dataset from Reddit scrape:\n")
    print(wsb_df.info(), "\n")
    print(wsb_df.head(), "\n")

    print("Dataset from AlphaVantage API:\n")
    print(l30d_df.info(), "\n")
    print(l30d_df.head(), "\n")

    print("Dataset from Yahoo Finance scrape:\n")
    print(yahoo_df.info(), "\n")
    print(yahoo_df.head(), "\n")

else:

    ################################################
    ##                                            ##
    ## PART 1: OBTAIN TICKERS FROM WALLSTREETBETS ##
    ##                                            ##
    ################################################

    # Obtain HTML elements from wallstreetbets using BeautifulSoup
    url = "https://ns.reddit.com/r/wallstreetbets/search/?sort=top&q=flair%3ADD&t=month&restrict_sr=on"
    headers = {'User-Agent': 'Mozilla/5.0'} # Simulate a browser visiting the page
    page = requests.get(url, headers = headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Initiate lists of tickers and list of common words to remove/neglect
    tickers = []
    tickers_unfiltered = []
    common = ["I", "AND", "THE", "A", "ARE", "IS", "US", "WSB", "DD", "WHO", "WHAT", "WHEN", "WHERE", "WHY", "HOW", "FINRA", "SEC", "WE", "YOU"]

    # Extract tickers from titles using regex (likely contains semantic errors) and append to tickers list
    links = soup.find_all("div", class_ = "search-result")
    for link in links:
        header = link.find("header", class_ = "search-result-header")
        title = header.findChildren("a", recursive = False)[0].contents[0]
        words = title.split()
        for word in words:
            ticker = re.findall(r"^[A-Z]{1,5}$|[$][A-Z]{1,5}", word) # (e.g. GME or $GME, but not gme nor $gme)
            
            if ticker:
                # Standardize ticker name and remove common words that are found by regex (e.g. "I", "AND", etc.)
                if "$" in ticker[0] and ticker[0][1:] not in common:
                    # Find number of upvotes if ticker is detected by program
                    upvotes = link.find("span", class_ = "search-score").contents[0].split()[0]
                    upvotes = int(upvotes.replace(",", "")) # Remove commas from integer and convert to integer
                    
                    tickers.append((ticker[0][1:], upvotes))
                    
                elif ticker[0] not in common:
                    # Find number of upvotes if ticker is detected by program
                    upvotes = link.find("span", class_ = "search-score").contents[0].split()[0]
                    upvotes = int(upvotes.replace(",", "")) # Remove commas from integer and convert to integer
                    
                    tickers.append((ticker[0], upvotes))

    # Store to local csv file
    wsb_df = pd.DataFrame(tickers, columns = ['Ticker', 'Upvotes'])
    wsb_df = wsb_df.groupby('Ticker').agg(sum).sort_values(by=['Upvotes'], ascending = False)
    wsb_df = wsb_df.reset_index()
    wsb_df.to_csv("datasets/wsb_dataset.csv")


    #####################################################################
    ##                                                                 ##
    ## PART 2: SEARCH FOR TICKER HISTORICAL PRICES ON ALPHAVANTAGE API ##
    ##                                                                 ##
    #####################################################################

    # API request
    test_stock = "GME" # For the final project, this section will be a function with tickers obtained earlier as inputs
    apikey = "AH70I7JMGOEK6EGE"
    stock_price = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=' + test_stock + '&apikey=' + apikey)
        
        # Remove non-existent stocks (not yet implemented)
        # Some invalid tickers (e.g. "KNOW") made it though the first filtering (semantic errors) and hence may cause
        # errors in AlphaVantage API
        
    # Initiate list of historical info
    last_30_days = []
        
    # Obtain stock price JSON last 30 days using datetime
    for i in range(0,31):
        day = datetime.today() - timedelta(days = i)
        
        # Account for days when the stock market is closed
        try:
            stock_daily = stock_price.json()["Time Series (Daily)"][day.strftime("%Y-%m-%d")]
        except:
            continue
            
        last_30_days.append((day.strftime("%Y-%m-%d"), stock_daily["4. close"], stock_daily["6. volume"]))

    # Store to local csv file
    l30d_df = pd.DataFrame(last_30_days, columns = ['Date', 'Close Price', 'Volume'])
    l30d_df.to_csv("datasets/l30d_dataset.csv")


    ######################################################
    ##                                                  ##
    ## PART 3: OBTAIN NEWS HEADLINES FROM YAHOO FINANCE ##
    ##                                                  ##
    ######################################################

    # Obtain HTML elements from Yahoo using BeautifulSoup
    test_stock = "GME" # For the final project, this section will be a function with tickers obtained earlier as inputs
    url = "https://finance.yahoo.com/quote/" + test_stock
    headers = {'User-Agent': 'Mozilla/5.0'} # Simulate a browser visiting the page
    page = requests.get(url, headers = headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Initiate lists of headlines
    headlines = []

    # Extract headlines from Yahoo finance
    headline_links = soup.find_all('a', class_ = "js-content-viewer")

    for headline in headline_links:
        headlines.append((headline.text, headline['href']))

    # Store to local csv file
    yahoo_df = pd.DataFrame(headlines, columns = ['Headline', 'Link'])
    yahoo_df.to_csv("datasets/yahoo_dataset.csv")

    
    # Print results depending on command-line inputs
    if args.scrape:
        print("Dataset from Reddit scrape:\n")
        print(wsb_df.info(), "\n")
        print(wsb_df.head(), "\n")

        print("Dataset from AlphaVantage API:\n")
        print(l30d_df.info(), "\n")
        print(l30d_df.head(), "\n")

        print("Dataset from Yahoo Finance scrape:\n")
        print(yahoo_df.info(), "\n")
        print(yahoo_df.head(), "\n")
    else:
        print("Dataset from Reddit scrape:\n")
        print(wsb_df, "\n")

        print("Dataset from AlphaVantage API:\n")
        print(l30d_df, "\n")

        print("Dataset from Yahoo Finance scrape:\n")
        print(yahoo_df, "\n")