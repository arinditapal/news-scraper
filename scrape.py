
import shutil
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import glob

## import scraping functions
# from times_of_india import times_of_india
# from india_today import india_today
# from the_economic_times import the_economic_times
# from hindustan_times import hindustan_times
from scrapers.the_hindu import the_hindu
from scrapers.dainik_bhaskar import dainik_bhaskar
from scrapers.the_indian_express import the_indian_express
from scrapers.helper import write_to_excel

# service = Service("./chromedriver-win64/chromedriver.exe")
# driver = webdriver.Chrome()

options = Options()
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options)


# list of news media to scrape from
# news_medias = ["hindustan times" ,"india today", "times of india", "the economic times"]
# news_medias = [ "the indian express", "dainik bhaskar", "the hindu"]
# news_medias = ["dainik bhaskar"]
# news_medias = ["the hindu"]
news_medias = ["the indian express"]

first_request = True
# scraping
for file_path in glob.glob("./under_process_disasters/*.txt"):
    year = file_path.split("\\")[-1].replace(".txt", '')

    # if input(f"Want to scrape from {year} : ") == "no":
    #     continue

    print("Processing year: ", year)

    with open(file_path, "r") as file:

        for line in file:
            if line == "\n":
                continue

            disaster = line.strip()
            news_article_objects = []
            article_id = 0

            print("\nProcessing disaster: ", disaster)
            
            for news_media in news_medias:
                print("\nProcessing news media: ", news_media)

                # preparing the google query
                query = f"news+articles+on+{disaster.replace(' ', '+')}+year+{year}+from+{news_media.replace(' ', '+')}"
                url = f"https://google.com/search?q={query}"


###########################   LOOP  #######################################
                # i number of time we go to next google page
                # i = 5
                # while i != 0: 
                try:
                    driver.get(url)
                except TimeoutError as e:
                    print("Timeout error")
                    continue

                # solving the capta manually, so block the code here
                # only first time this input is required because capta only apears once 
                if first_request:
                    input("solve capta: ")
                    first_request = False
                time.sleep(2)

                ##
                ## this is where i come back if next button on google search is pressed.
                # now the google page is loaded and we search of a perticular div
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "A6K0A"))
                    )
                except:
                    continue

                soup = BeautifulSoup(driver.page_source, features = "html.parser")

                articles = soup.find_all("div", class_="A6K0A")

                print("Total articles on google search page found: ", len(articles))

                for article in articles:
                    print("\nInvestigate an google div.")

                    # extract news media name
                    div_contains_news_media = article.find("span", class_="VuuXrf")

                    if div_contains_news_media == None:
                        print("This may be dropdown or video, so moving on.")
                        continue

                    article_news_media = div_contains_news_media.text.lower()

                    print("Media publishing the article is: ", article_news_media)
                    
                    # checking news media name with current new media under processing
                    if news_media in article_news_media:
                        article_url = article.find("a")["href"]
                        print(type(article_url), article_url)

                        if news_media == "times of india":
                            news_article_object = times_of_india(driver, article_url)
                            if news_article_object:
                                news_article_objects.append(news_article_object)

                        elif news_media == "india today":
                            news_article_object = india_today(driver, article_url)
                            if news_article_object:
                                news_article_objects.append(news_article_object)
                                
                        elif news_media == "the economic times":
                            news_article_object = the_economic_times(driver, article_url)
                            if news_article_object:
                                news_article_objects.append(news_article_object)

                        elif news_media == "hindustan times":
                            news_article_object = hindustan_times(driver, article_url)
                            if news_article_object:
                                news_article_objects.append(news_article_object)

                        elif news_media == "the hindu":
                            news_article_object = the_hindu(driver, article_url)
                            if news_article_object:
                                news_article_objects.append(news_article_object)

                                # target folder
                                path = f'./images/{year}/{disaster}/{news_media}/article_{article_id + 1}'
                                os.makedirs(path, exist_ok = True)

                                # source folder
                                source = f"./temp_image_store/"

                                # get file in source folders
                                files = os.listdir(source)

                                for file in files:
                                    shutil.move(os.path.join(source, file), path)
                                article_id += 1

                        elif news_media == "dainik bhaskar":
                            news_article_object = dainik_bhaskar(driver, article_url)
                            if news_article_object:
                                news_article_objects.append(news_article_object)

                                # target folder
                                path = f"./images/{year}/{disaster}/{news_media}/article_{article_id + 1}/"
                                os.makedirs(path, exist_ok = True)

                                # source folder
                                source = f"./temp_image_store/"

                                # get file in source folders
                                files = os.listdir(source)

                                for file in files:
                                    shutil.move(os.path.join(source, file), path)
                                article_id += 1

                        elif news_media == "the indian express":
                            news_article_object = the_indian_express(driver, article_url)
                            if news_article_object:

                                # target folder
                                path = f"./images/{year}/{disaster}/{news_media}/article_{article_id + 1}/"
                                os.makedirs(path, exist_ok = True)

                                # source folder
                                source = f"./temp_image_store/"

                                # get file in source folders
                                files = os.listdir(source)

                                for file in files:
                                    shutil.move(os.path.join(source, file), path)

                                news_article_object["image_folder_path"] = path
                                # news_article_objects.append(news_article_object)
                                article_id += 1

                    else:
                        print("Not the media we need. Moving one.")
                        continue

                
                if news_article_objects:
                    # length shows no. of articles extracted
                    print("\nArticles scraped are: ", len(news_article_objects))

                    output_file = f"./news/{year}/{disaster}.xlsx"

                    write_to_excel(news_article_objects, output_file)

                    news_article_objects = []
                    print(f"\n\n Wrote to {disaster}.xlsx\n\n")
                




