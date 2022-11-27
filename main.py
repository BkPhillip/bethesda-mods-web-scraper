"""
Bethesda Mods Web Scraper
by Bryson Phillip
11/22/22

"""
# todo: Move app class to other file and import
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
        self.url = "https://mods.bethesda.net/en/?number_results=&order=&page=1&platform=&product=&sort=&text="

    def get_new_mods(self, save_path,  quantity, order, console, game, sort, period,  search_term):
        search_options = {"results=": quantity,
                          "order=": order,
                          "platform=": console,
                          "product=": game,  # Need to change url at .net/en/<game_name> rather than at product=
                          "sort=": sort,
                          "text=": search_term}

        for option in search_options:
            if option == "product=":
                url_index1 = self.url.index("/en/") + len("/en/")
                url_index2 = self.url.index(option) + len(option)  # get index after last character of string in URL
                self.url = self.url[:url_index1] + search_options[option] + self.url[url_index1:]
                self.url = self.url[:url_index2] + search_options[option] + self.url[url_index2:]
            elif option == "sort=" and period != "all time" and search_options[option] != "Date":
                url_index = self.url.index(option) + len(option)  # get index after last character of string in URL
                self.url = self.url[:url_index] + search_options[option] + f"-{period}" + self.url[url_index:]
            else:
                url_index = self.url.index(option) + len(option)  # get index after last character of string in URL
                self.url = self.url[:url_index] + search_options[option] + self.url[url_index:]

        self.driver.get(self.url)

        sleep(7)  # Time for javascript to load

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
        df.to_csv(save_path)

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
        # Platform (XboxOne, Playstation4, WINDOWS)
        platform_list = ["XB1", "PS4", "WINDOWS"]
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
        sort_list = ["Date", "Most Popular", "Highest Rated", "Most Favorited"]
        self.sort_combobox = ttk.Combobox(master, values=sort_list)
        self.sort_combobox.current(0)
        self.sort_combobox.pack()
        # Time Period (daily, weekly, monthly, all time)
        period_list = ["day", "week", "month", "all time"]
        self.period_combobox = ttk.Combobox(master, values=period_list, state="disabled")
        self.period_combobox.current(3)
        self.period_combobox.pack()
        # Search Term
        search_label = tk.Label(master, text="Search:")
        search_label.pack()
        self.search_entry = tk.Entry(master, width=20)
        self.search_entry.pack()
        # Button to  get results and run bot
        button = tk.Button(master, text="Find Mods", command=self.create_csv)
        button.pack()

        self.sort_combobox.bind('<<ComboboxSelected>>', self.change_sort)
        frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    def create_csv(self):
        save_path = fd.asksaveasfile(mode="w", initialfile="mod-data.csv", defaultextension=".csv")
        # Get  widget values to make url search
        results = str(self.results.get())  # Get desired results quantity
        order = self.order.get()  # Ascending or Descending
        platform = self.platform_combobox.get()  # get console name
        game = self.game.get()  # Fallout 4 or Skyrim
        match self.sort_combobox.current():  # Get sort choice from list
            case 0:
                sort = "published"
            case 1:
                sort = "popular"
            case 2:
                sort = "rating"
            case 3:
                sort = "follow"
        period = self.period_combobox.get()  # Get period choice from list
        search_term = self.search_entry.get()  # Get Search Term

        bot = FalloutXboxModsScraper(CHROME_DRIVER_PATH)
        bot.get_new_mods(save_path, results, order, platform, game, sort, period, search_term)

    def change_sort(self, event):
        if self.sort_combobox.get() == "Date":
            self.period_combobox.config(state='disabled')
        else:
            self.period_combobox.config(state="normal")


root = tk.Tk()
root.title("Bethesda Mods Web Scraper")

window = Window(root)
root.mainloop()
