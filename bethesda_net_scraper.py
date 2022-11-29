from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd


class BethesdaNetScraper:
    def __init__(self, driver_path):
        self.driver = webdriver.Chrome(executable_path=driver_path)
        self.url = "https://mods.bethesda.net/en/?number_results=&order=&page=1&platform=&product=&sort=&text="

    def get_new_mods(self, save_path,  quantity, order, console, game, sort, period,  search_term, categories):
        search_options = {"results=": quantity,
                          "order=": order,
                          "platform=": console,
                          "product=": game,
                          "sort=": sort,
                          "text=": search_term}

        for option in search_options:
            if option == "product=":  # Game name inserted into url at 2 places, all others options at one url index
                url_index = self.url.index("/en/") + len("/en/")
                url_index2 = self.url.index(option) + len(option)  # get index after last character of string in URL
                self.url = self.url[:url_index] + search_options[option] + self.url[url_index:]
                self.url = self.url[:url_index2] + search_options[option] + self.url[url_index2:]
            elif option == "sort=" and period != "all time" and search_options[option] != "Date":  # Time period options
                url_index = self.url.index(option) + len(option)  # get index after last character of string in URL
                self.url = self.url[:url_index] + search_options[option] + f"-{period}" + self.url[url_index:]
            else:
                url_index = self.url.index(option) + len(option)  # get index after last character of string in URL
                self.url = self.url[:url_index] + search_options[option] + self.url[url_index:] # Insert option into url

        if categories:  # check if any categories were selected
            for category in categories:
                cat_no_spaces = category.replace(" ", "%20").replace("/", "%2F")  # Remove " " and "/" from strings
                url_index = self.url.index("number_results")  # Get url index
                self.url = self.url[:url_index] + f"category={cat_no_spaces}&" + self.url[url_index:]

        self.driver.get(self.url)  # Open web driver

        sleep(5)  # Time for javascript to load

        mod_titles = [title.text for title in self.driver.find_elements(By.CSS_SELECTOR, "div.card-name p")]
        mod_authors = [author.text for author in self.driver.find_elements(By.CSS_SELECTOR, "div.card-user p")]
        mod_ratings = [float(rating.get_attribute('rating')) for rating in
                       self.driver.find_elements(By.CSS_SELECTOR, "div.card-rating")]
        mod_review_counts = [review_count.text[1:-1] for review_count in
                             self.driver.find_elements(By.CSS_SELECTOR, "div.card-rating span.rating-average-number")]
        mod_links = [link.get_attribute("href") for link in
                     self.driver.find_elements(By.CSS_SELECTOR, "div.content-module > a")]

        # Remove "k" from values so sheet can be properly sorted, e.i. 101k -> 101000
        count_values = []
        for count in mod_review_counts:
            try:
                count_values.append(int(count))
            except ValueError:
                count_values.append(int(count.replace("k", "")) * 1000)

        # Add data to dictionary, convert to DataFrame, and save to csv
        data = {"Name": mod_titles,
                "Author": mod_authors,
                "Rating": mod_ratings,
                "Review Count": count_values,
                "Link": mod_links}
        df = pd.DataFrame.from_dict(data)
        df.to_csv(save_path)

        self.driver.quit()
