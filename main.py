from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd

CHROME_DRIVER_PATH = "/Users/BrysonPhillip/Development/chromedriver"


class FalloutXboxModsScraper:
    def __init__(self, driver_path):
        self.driver = webdriver.Chrome(executable_path=driver_path)
        self.url = "https://mods.bethesda.net/en/fallout4?number_results=&order=&page=1&platform=&product=&sort=&text="

    def get_new_mods(self, quantity, order, console, game, sort, search_term):

        search_options = {"results=": quantity,
                          "order=": order,
                          "platform=": console,
                          "product=": game,  # Need to change url at .net/en/<game_name> rather than at product=
                          "sort=": sort,
                          "text=": search_term}

        for option in search_options:
            url_index = self.url.index(option) + len(option)  # get index after last character of string in URL
            self.url = self.url[:url_index] + search_options[option] + self.url[url_index:]

        self.driver.get(self.url)

        sleep(7)

        mod_titles = [title.text for title in self.driver.find_elements(By.CSS_SELECTOR, "div.card-name p")]
        mod_authors = [author.text for author in self.driver.find_elements(By.CSS_SELECTOR, "div.card-user p")]
        mod_ratings = [float(rating.get_attribute('rating')) for rating in
                       self.driver.find_elements(By.CSS_SELECTOR, "div.card-rating")]
        mod_review_counts = [int(review_count.text[1:-1]) for review_count in
                             self.driver.find_elements(By.CSS_SELECTOR, "div.card-rating span.rating-average-number")]
        mod_links = [link.get_attribute("href") for link in
                     self.driver.find_elements(By.CSS_SELECTOR, "div.content-module > a")]

        data = {"Name": mod_titles,
                "Author": mod_authors,
                "Rating": mod_ratings,
                "Review Count": mod_review_counts,
                "Link": mod_links}

        df = pd.DataFrame.from_dict(data)
        df.to_csv("mod-data.csv")

        self.driver.quit()


bot = FalloutXboxModsScraper(CHROME_DRIVER_PATH)
bot.get_new_mods("60", "desc", "PS4", "fallout4", "published", "")
