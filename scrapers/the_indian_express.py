


# imports
from selenium import webdriver
from scrapers.helper import detect
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import os
import json
import re
import time


# global variables (temporary)
# url = "https://indianexpress.com/article/explained/explained-climate/darjeeling-rain-landslides-deadly-for-india-10289158/"
# url = "https://indianexpress.com/article/cities/kolkata/north-bengal-rainfall-kalimpong-darjeeling-live-updates-landslides-damages-deaths-10288611/"
# url = "https://indianexpress.com/article/india/cyclone-montha-live-updates-landfall-andhra-pradesh-coast-imd-10329039/"
# driver = webdriver.Chrome()


# function starts ...
def the_indian_express(driver, url):

    # open the page
    # use the driver to open the webpage
    try:
        driver.get(url)
        print("loading....complete")
    except TimeoutError as e:
        print("Timeout has occured while loading the page.")
        return None


    # grab hold of the html of webpage
    soup = BeautifulSoup(driver.page_source, features = "html.parser")

    title = ""
    date = ""
    description = ""
    body = ""
    extra_body = ""
    path = ""
    count_of_img = 0
    meta_data = {}
    img_tags = []
    path = "./temp_image_store/"
    # caption = ""


    # scrape


    # scrape title
    # <title> tag
    if detect(driver, By.TAG_NAME, "title"):
        tag = soup.select_one('title')
        if tag:
            title = tag.text
            print("title: ", title)



    # scrape date
    # <meta itemprop="datePublished" content="2025-10-27T10:26:04+05:30">
    if detect(driver, By.CSS_SELECTOR, 'meta[itemprop="datePublished"]'):
        # print("DETECTED DATE")
        tag = soup.select_one('meta[itemprop="datePublished"]')
        if tag:
            date = tag["content"]
            print("date: ", date)
            year = date.split('-')[0]
        # print(year)

    # scrape description
    # <meta name="description" content="The Met Department forecast heavy rains across several places of the southern state under the influence of Montha.">
    if detect(driver, By.CSS_SELECTOR, 'meta[name="description"]'):
        tag = soup.select_one('meta[name="description"]')
        if tag:
            description = tag["content"]
            print("description: ", description[:10])


    # scrape content
    # <div class="articles">
    if detect(driver, By.CSS_SELECTOR, 'div.articles'):
    
        tag = soup.select_one('div.articles')
        if tag:
            content = tag.get_text(strip = True)
            print("content: ", content[:10])

    elif detect(driver, By.CLASS_NAME, "story_details"):
        tag = soup.select_one('div.story_details')
        if tag:
            content = tag.get_text(strip = True)
            print("content: ", content[:20])


    # scape image
    if detect(driver, By.CLASS_NAME, "custom-caption"):
        tag = soup.select_one('span.custom-caption')
        if tag:
            img_tags.append(tag.img)


    # scrape images from live blog divs
    if detect(driver, By.CSS_SELECTOR, 'div.liveblog-feed'):
        tag = soup.select_one('div.liveblog-feed')
        if tag:
            para_tags = tag.find_all('p')
            if para_tags:
                for para_tag in para_tags:
                    try:
                        img_tag =  para_tag.img
                    except:
                        continue
                    if img_tag:
                        img_tags.append(img_tag)

    print("num of images found: ", len(img_tags))
    if img_tags:
        for img in img_tags:
            src = img["src"]

            try:
                alt = img["alt"]
            except:
                pass

            image_name = f'image_{count_of_img + 1}.jpg'

            try:
                driver.get(src)
                time.sleep(2)
            except:
                continue

            try:
                driver.save_screenshot(path + image_name)
            except:
                continue

            meta_data[count_of_img + 1] = { 
                "src": src, 
                "alt": alt
                }
            count_of_img += 1

    with open(f"{path}meta_data.json", 'w') as file:
        json.dump(meta_data, file)

    news_article_object = {
        "title": title,
        "date": date,
        "news_media": "The Hindu",
        "url": url,
        "content": body + extra_body,
        "description": description,
        "image_folder_path": path,
        "# image": count_of_img
    }

    return news_article_object
        