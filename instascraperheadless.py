from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as soup
import csv
import time
import re
import datetime
from datetime import date
import pymysql
import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='instascraper')


def create_database(tblName="instatemplate"):
    #Create a cursor for the database
    cur = connection.cursor()

    try:
        #Create a table in mysql
        createsql = "CREATE TABLE %s ( \
          `post_id` int(11) DEFAULT NULL, \
          `url` varchar(255) DEFAULT NULL, \
          `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, \
          `date_time` varchar(255) DEFAULT NULL, \
          `media` varchar(255) DEFAULT NULL, \
          `likes` int(11) DEFAULT NULL, \
          `views` int(11) DEFAULT NULL, \
          UNIQUE (url) \
        )" % (tblName)

        cur.execute(createsql)
    except pymysql.err.InternalError as e:
        code, msg = e.args
        if code == 1050:
            print(tblName, 'already exists')
        else:
            raise

def writedata(instaname, post_id=2,url='url',date_time='2018-05-08 18:37:43.000' ,media='photo',likes=10,views=89):
    cur = connection.cursor()
    try:

        if views != None:
            sql = "INSERT INTO %s(post_id,url,date_time,media,likes,views) \
   VALUES ('%d', '%s', '%s', '%s', '%d', '%d' )" % (instaname, post_id, url, date_time, media, likes, views)
        else:
            sql = "INSERT INTO %s(post_id,url,date_time,media,likes) \
   VALUES ('%d', '%s', '%s', '%s', '%d')" % (instaname, post_id, url, date_time, media, likes)

        cur.execute(sql)

    except pymysql.err.IntegrityError as e:
        code, msg = e.args
        if code == 1062:
            print(msg)
            pass
        else:
            raise

    
    connection.commit()
    



def getinstagram_data():
    data_list = []
    numgrab = int(input("Enter number of posts to scrape: "))
    link = (input("Enter INSTAGRAM URL: "))
    instaname = link.split("/")[3]
    create_database(instaname)

    print(data_list)
    chromedriver = '/Users/Username/Downloads/chromedriver'
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  
    options.add_argument('window-size=1200x600')  
    driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)

    driver.get(link)
    
    oldsource = driver.page_source
    oldsoup = soup(oldsource, "html.parser")
    fstring = oldsoup.body.script.text
    i = fstring.find('"count"')
    igfollowers = re.sub("[^0-9]", "", fstring[i+8:i+16])

    #Takes to first post
    driver.find_element_by_xpath('//div[contains(@class,"eLAPa")]').click()
    time.sleep(2)


    for i in range(numgrab):

        newsource = driver.page_source
        newsoup = soup(newsource, "html.parser")

        while newsoup == oldsoup:
            time.sleep(0.1)
            newsource = driver.page_source
            newsoup = soup(newsource, "html.parser")
            if newsoup != oldsoup:
                break


        oldsource = driver.page_source
        oldsoup = soup(oldsource, "html.parser")
        postnum = i + 1
        if oldsoup.findAll("span",{"class":"vcOH2"}):
            mediatype = "video"
        elif oldsoup.findAll("span",{"class":"zV_Nj"}):
            mediatype = "photo"
        elif oldsoup.findAll("div",{"class":"_3gwk6"}):
            mediatype = "photofewlikes"
        else:
            mediatype = "photonolikes"

        date_time_raw = oldsoup.findAll("time",{"class":"_1o9PC Nzb55"})[0]['datetime']
        date_time = date_time_raw.replace('T', ' ').replace('Z','')

        if mediatype == "photo":
            media = "PHOTO"
            photolikestring = driver.find_element_by_xpath('//span[contains(@class,"zV_Nj")]').text
            photolikes = re.sub("[^0-9]", "", photolikestring)
            post_info = [postnum, driver.current_url, date_time, media, int(photolikes), None ]
            print(post_info)
            #Write the data to MySQL
            writedata(instaname, postnum, driver.current_url, date_time, media, int(photolikes), None)
            data_list.append(post_info)
        elif mediatype == "photofewlikes":
            media = "PHOTO"
            photolikes = 0
            likecontainer = oldsoup.findAll("div",{"class":"_3gwk6"})[0].find_all("a")
            for i in likecontainer:
                photolikes += 1
            post_info = [postnum, driver.current_url, date_time, media, photolikes, None ]
        elif mediatype == "video":
            media = "VIDEO"
            viewstring = driver.find_element_by_xpath('//span[contains(@class,"vcOH2")]').text
            videoviews = re.sub("[^0-9]", "", viewstring)
            driver.find_element_by_xpath('//span[contains(@class,"vcOH2")]').click()
            likestring = driver.find_element_by_xpath('//div[contains(@class,"vJRqr")]').text
            likes = re.sub("[^0-9]", "", likestring)
            driver.find_element_by_xpath('/html/body').click()
            post_info = [postnum, driver.current_url, date_time, media, int(likes), int(videoviews)]
            print(post_info)
            #Write the data to MySQL
            writedata(instaname, postnum, driver.current_url, date_time, media, int(likes), int(videoviews))
            data_list.append(post_info)
        elif mediatype == "photonolikes":
            media = 'PHOTO'
            photolikes = 0
            

        driver.find_element_by_xpath('/html/body').send_keys(Keys.ARROW_RIGHT)
        time.sleep(2)

    driver.close()
    return data_list



thedata = getinstagram_data()



connection.close()


