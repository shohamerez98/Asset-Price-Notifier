import requests
import os
import smtplib
import datetime as dt


# setup constans
MY_EMAIL = "realtwentydust@gmail.com"
RECEIVER = "shohamerez98@gmail.com"
MY_PASSWORD = "pzilmfxajxhoukji" #os.environ.get("PASSWORD")
STOCK_API_KEY = "T0KHR8TYOWMBF3VU"  #"5OO8NA3HM6S91O5L"  "FDC35JWAG9UNUWIZ"
NEWS_API_KEY = "cc7d1dd1b0a4402a87abb1604761d062"
STOCK_TICKERS = ["VOO","NDAQ"]
CRPYTO_TICKERS = ["BTC"]

# setup vars
alert_list = []
crypto_dic = {}
stock_dict = {}
news_exist = False

# setup functions
def send_mail(sub,content):
  with smtplib.SMTP("smtp.gmail.com") as connection:
    connection.starttls()
    connection.login(user=MY_EMAIL, password=MY_PASSWORD)
    connection.sendmail(from_addr=MY_EMAIL, to_addrs=RECEIVER, msg=f"Subject:{sub}\n\n{content}")

def check_today_date():
  today = dt.datetime.now()
  today = str(today)
  date = today.split(" ")[0]
  return date

def check_yesterday_date(status):
  today = dt.datetime.now() - dt.timedelta(1)
  day_name = today.strftime("%A")

  if status == "stock" and day_name == "Monday": # check also for a monday, meaning last day of stock trading was friday
    yesterday_date = dt.datetime.now() - dt.timedelta(3)
    yesterday = yesterday_date.strftime('%Y-%m-%d')
    return yesterday
    print(yesterday)
  else: # last trading day is yesterday
    yesterday_date = today - dt.timedelta(1)
    yesterday = yesterday_date.strftime('%Y-%m-%d')
    return yesterday


def check_for_change(dictionary):
  global alert_list
  print(dictionary)
  for stock in dictionary:
    print(stock)
    change_percent = dictionary[stock]['% Change']
    if abs(change_percent) >= 7:
      alert_list.append(stock)

# setup message pattern
today_date = check_today_date()
message = f"Alert regarding price change of the following assests (updated for {today_date}):"
subject = "Stock/Crypto price update"


# make API requests for stock information on daily basis
for stock_symbol in STOCK_TICKERS:
  stock_response = requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_symbol}&apikey={STOCK_API_KEY}")
  stock_response.raise_for_status()
  stock_data = stock_response.json()

  # obtain data from json
  date = check_today_date()
  open_price_stock = stock_data['Time Series (Daily)'][date]['1. open']
  open_price_stock = float(open_price_stock)
  close_price_stock = stock_data['Time Series (Daily)'][date]['4. close']
  close_price_stock = float(close_price_stock)

  try: # check if there has been dividend paid.
    dividend = stock_data['Time Series (Daily)'][date]['7. dividend amount']
  except KeyError: # No dividend entry for that stock
    dividend = 0


  # get yesterday price
  yesterday_date = check_yesterday_date("stock")
  print(yesterday_date)
  yesterday_close_price_stock = float(stock_data['Time Series (Daily)'][yesterday_date]['4. close'])

  # calculate percentage of change
  diff_stock_price = yesterday_close_price_stock - close_price_stock # amount in USD
  change_in_stock_price = ((close_price_stock - yesterday_close_price_stock) / abs(yesterday_close_price_stock)) * 100 # change in percentage

  # save data in dictionary
  stock_dict[stock_symbol] = {'Current Date':date,
                              'Open Price':open_price_stock,
                              'Close Price':close_price_stock,
                              'Yesterday Price': yesterday_close_price_stock,
                              'Dividend Paid':dividend,
                              '% Change': change_in_stock_price,
                              'Difference': diff_stock_price
                             }


# make API request for cryptocurrencies
crypto_api_params = {
  "function":"DIGITAL_CURRENCY_DAILY",
  "symbol":"",
  "market":'usd',
  "apikey": STOCK_API_KEY
}


for crypto in CRPYTO_TICKERS:
  crypto_api_params['symbol'] = crypto
  crypto_response = requests.get("https://www.alphavantage.co/query", params=crypto_api_params)
  crypto_data = crypto_response.json()
  today_date = check_today_date()
  yesterday_date = check_yesterday_date("crypto")

  # obtain data from json
  today_close_price_crypto = crypto_data['Time Series (Digital Currency Daily)'][yesterday_date]['4b. close (USD)']
  today_close_price_crypto = float(today_close_price_crypto)
  yesterday_close_price_crypto = crypto_data['Time Series (Digital Currency Daily)'][yesterday_date]['4b. close (USD)']
  yesterday_close_price_crypto  = float(yesterday_close_price_crypto)
  print(today_close_price_crypto)
  # calculate difference
  crypto_diff_price = today_close_price_crypto - yesterday_close_price_crypto # amount in USD
  change_in_crypto_price = ((today_close_price_crypto - yesterday_close_price_crypto) * abs(yesterday_close_price_crypto)) * 100 # change in %

  # save data into dictionary
  crypto_dic[crypto] = {'Current Price':today_close_price_crypto,
                       'Yesterday Price': yesterday_close_price_crypto,
                       'Price difference': crypto_diff_price,
                        '% Change':change_in_crypto_price
                       }


# make API requests for news
today_date = check_today_date()
news_dict = {}
for stock in STOCK_TICKERS:
  news_api_params = {"q":stock,
                    "from":today_date,
                    "language":"en",
                     "sortBy":"popularity",
                    "apikey":NEWS_API_KEY
                    }
  news_response = requests.get("https://newsapi.org/v2/everything", params = news_api_params)
  news_data = news_response.json()['articles'][:1]

  if stock in alert_list:
    try:
      news_dict[stock] = {"title":news_data['title'],
                        "description":news_data['description'],
                        "url":news_data['url']
                       }
      news_exist = True
    except TypeError:
      news_dict = {}
      print("Error happened")
      news_exist = False


# now check if conditions are met to send an alert
check_for_change(stock_dict)
check_for_change(crypto_dic)

news_message = ""
for ticker in alert_list:
  if ticker in crypto_dic:
    if crypto_dic[ticker]['% Change'] < 0:
        message += f"\nPrice change for {ticker}! Price dropped by {crypto_dic[ticker]['% Change']}% and priced {crypto_dic[ticker]['Current Price']}$."
    else:
        message += f"\nPrice change for {ticker}! Price rised by {crypto_dic[ticker]['% Change']}% and priced {crypto_dic[ticker]['Current Price']}$."

  elif ticker in stock_dict:
    # check if change was up or down
    asset_list_len = len(alert_list)

    if stock_dict[ticker]['% Change'] < 0:
        message += f"\nPrice change for {ticker}! Price rised by {stock_dict[ticker]['% Change']}% and priced {stock_dict[ticker]['Close Price']}$."
    else:
        message += f"\nPrice change for {ticker}! Price dropped by {stock_dict[ticker]['% Change']}% and priced {stock_dict[ticker]['Close Price']}$."

  elif asset_list_len == 0: # meaning no asset has majorly changed in value
    message = "Looks like nothing special happened today in the markets."
  # now add a link to 1 major article for every ticker:

  if news_exist:
    news_message += f"\nHere's an article about {ticker}:\n\nTitle: {news_dict[ticker]['title']}\nSummary:{news_dict[ticker]['description']}\nLink:{news_dict[ticker]['url']} "
    message += news_message

#finally send mail
send_mail(subject,message)
