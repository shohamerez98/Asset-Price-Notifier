# Asset-Price-Notifier
#As a finance enthusiaist, I love to track my assests performance from time to time. 
However, when something unusual happens in the markets, let's say NASDAQ rises by 10% a day - I want to know it, and even check the latest news regarding it. 
This little project comes to solve just that! 

The concept is quite simple:
  1) Obtain data from API regarding stocks and other assets' performance.
  2) Compare the asset's closing price from today with the closing price from previous trading day.
  3) User can manually change the list of assets to be tracked.
  4) If there is aove 7% change in price (up or down) - a notification is requested. (The trigger for notification can be modified)
  5) Send an automated email containig only the assets that have changed in price by the criteria.
