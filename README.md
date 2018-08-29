# Instascraper
Python script to scrape post data from an Instagram user using Selenium Webdriver with Chrome and writes the data into a SQL file


Necessary python packages
* selenium
* beautifulsoup4
* pymysql

Must have Chromedriver installed
http://chromedriver.chromium.org/

# Things to Change
Lines 13-16 - Change to the location of your database

Line 79 - Change the path to the location of your Chromedriver file 

# NB
This script requires some knowledge of python and HTML/CSS to use. The HTML code of instagram can change at any time and render this script defunct. 
If the script has stopped working, then that will be because the script will not be able to find the correct data in the HTML code due to the element tags changing. The script must then be updated to correspond with the correct code in the instagram HTML.


