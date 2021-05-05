This script has the following command-line uses:

    1. python scraper.py
        this scrapes and prints out all three obtained datasets in full

    2. python scraper.py --scrape
        this scrapes and prints out basic info of obtained datasets along with a sample of each dataset

    3. python scraper.py --static filepath
        this skips all the scraping and accesses local csv datasets to print out basic info and dataset samples
        for this program, scraped datasets are stored as csv files in "datasets/" folder
        therefore, one would run the command-line like so: python scraper.py --static datasets

Details:
Purpose: the purpose of my final project is to find popular stock tickers from Reddit's r/wallstreetbets based on the number of upvotes. With the tickers, I will use the AlphaVantage API to find historical data of price and volume in order to graph the change over time. Moreover, I will use the tickers to find relevant news headlines from Yahoo Finance.
The point is to see whether macroeconomics or social media have an effect on stock price and volume or vice versa.

    Part 1:
        The first part of this program scrapes the monthly top posts from Reddit's r/wallstreetbets's DD (due diligence) flair filter.
            url: https://ns.reddit.com/r/wallstreetbets/search/?sort=top&q=flair%3ADD&t=month&restrict_sr=on
        The reason to use the DD filter is because DD posts, in my opinion, are more "serious" posts that will offer better insight into which stocks people are investing in.
        The program targets post titles and upvote counts to extract possible ticker symbols and number of upvotes as a measure of popularity.
        The output of the first part is a dataframe containing two columns: Ticker and Upvotes
        Due to semantic errors, some ticker symbols may be neglected (e.g. the stock ticker "A" just so happens to be a common word, which I decided to filter out) and some randomly capitalized non-ticker words may be included (e.g. acronyms and abbreviations).

    Part 2:
        The second part of this program obtains stock data of a placeholder ticker, GME, via the AlphaVantage API.
            documentation: https://www.alphavantage.co/documentation/
        The data of interest is daily close price and volume for the last 30 days.
        The output of the second part is a dataframe with three columns: Date, Close Price, Volume.
        In the final project, this second part will be in the form of a function to allow for iteration through the dataframe from the first part to get stock data for each identified ticker symbol (and remove invalid ones).
        For each symbol, I plan on plotting a time series to show Close Price and Volume over time.

    Part 3:
        The last part of this program finds and extracts news headlines from Yahoo Finance's GME page (as a placeholder)
            url: https://finance.yahoo.com/quote/GME/
        In the final project, this part will also be in a form of a function so that it can iterate through the dataframe from the first part to get news headlines for each stock ticker (and also remove invalid tickers).
