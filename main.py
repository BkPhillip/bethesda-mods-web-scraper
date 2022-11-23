"""
Bethesda Mods Web Scraper
by Bryson Phillip
11/22/22

"""
# todo: Open filedialog for ability to name and choose location of saved file
# todo: Time-period combo box
# todo: Make Time-period combo box not appear when date published sorting option is selected
# todo: change number of ratings from k's to 1000's
# todo: categories option from option box, "category=<category>&" inserted before "number_

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
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
        mod_review_counts = [review_count.text[1:-1] for review_count in
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


class Window:
    def __init__(self, master):
        frame = tk.Frame(master, width=200, height=200)
        # Results Quantity
        self.results = tk.IntVar()
        self.results.set(20)
        results_spinbox = tk.Spinbox(master, from_=1, to=1000, increment=1, textvariable=self.results)
        results_spinbox.pack()
        # Ascending or Descending Order
        self.order = tk.StringVar(None, "desc")
        asc_radio = tk.Radiobutton(master, text="Ascending", variable=self.order, value="asc")
        asc_radio.pack()
        desc_radio = tk.Radiobutton(master, text="Descending", variable=self.order, value="desc")
        desc_radio.pack()
        # Platform (XboxOne, Playstation4, PC)
        platform_list = ["XB1", "PS4", "PC"]
        self.platform_combobox = ttk.Combobox(master, values=platform_list)
        self.platform_combobox.current(0)
        self.platform_combobox.pack()
        # Game(Fallout4, Skyrim)
        self.game = tk.StringVar(None, "fallout4")
        fallout4_radio = tk.Radiobutton(master, text="Fallout 4", variable=self.game, value="fallout4")
        fallout4_radio.pack()
        skyrim_radio = tk.Radiobutton(master, text="Skyrim", variable=self.game, value="skyrim")
        skyrim_radio.pack()
        # Sorting Options (date added, most popular, highest rated, most favorited)
        sort_list = ["published", "popular", "rating", "follow"]
        self.sort_combobox = ttk.Combobox(master, values=sort_list)
        self.sort_combobox.current(0)
        self.sort_combobox.pack()
        # Search Term
        search_label = tk.Label(master, text="Search:")
        search_label.pack()
        self.search_entry = tk.Entry(master, width=20)
        self.search_entry.pack()
        # Button to  get results and run bot
        button = tk.Button(master, text="Find Mods", command=self.create_csv)
        button.pack()

        frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    def create_csv(self):
        results = str(self.results.get())  # Get desired results quantity
        order = self.order.get()  # Ascending or Descending
        platform = self.platform_combobox.get()  # get console name
        game = self.game.get()  # Fallout 4 or Skyrim
        sort = self.sort_combobox.get()  # Get sort choice from list
        search_term = self.search_entry.get()  # Get Search Term

        bot = FalloutXboxModsScraper(CHROME_DRIVER_PATH)
        bot.get_new_mods(results, order, platform, game, sort, search_term)


root = tk.Tk()
root.title("Bethesda Mods Web Scraper")

window = Window(root)
root.mainloop()
