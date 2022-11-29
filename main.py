"""
Bethesda Mods Web Scraper
by Bryson Phillip
11/22/22

"""
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from bethesda_net_scraper import BethesdaNetScraper
from dotenv import load_dotenv
import os

load_dotenv()
CHROME_DRIVER_PATH = os.environ['CHROME_DRIVER_PATH']


class Window:
    def __init__(self, master):
        frame = tk.Frame(master, width=200, height=80)
        # Results Quantity
        results_label = tk.Label(master, text="Results:")
        results_label.pack()
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
        sort_label = tk.Label(master, text="Sort:")
        sort_label.pack()
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
        # Categories (select as many as desired)
        cat_label = tk.Label(master, text="Categories:")
        cat_label.pack()
        categories = ["Animals", "Armor", "Audio", "Automatron", "Buildings", "Characters", "Cheats", "Clothing",
                      "Collectibles", "Companions", "Contraptions Workshop", "Crafting", "Creatures", "Environmental",
                      "Far Harbor", "Foliage", "Followers", "Gameplay", "Graphics", "Hair and Face", "Homes",
                      "Immersion", "Items and Objects - Player", "Items and Object - World", "Landscape", "Misc",
                      "Modder Resources/Tutorials", "Models and Textures", "NPCs", "Nuka-World", "Nvidia", "Overhaul",
                      "Patches", "Perks", "Power Armor", "Quests", "Races", "Radio", "Settlements",
                      "Skills and Leveling", "Towns", "UI", "Utilities", "Vault-Tec Workshop", "Wasteland Workshop",
                      "Weapons", "Work-In-Progress", "Workshop", "Worlds"]
        var = tk.Variable(value=categories)
        self.categories_listbox = tk.Listbox(master,
                                             listvariable=var,
                                             height=24,
                                             selectmode="multiple",
                                             )
        self.categories_listbox.pack(pady=10)
        # Button to  get results and run bot
        button = tk.Button(master, text="Find Mods", command=self.create_csv)
        button.pack()
        # Bindings
        self.sort_combobox.bind('<<ComboboxSelected>>', self.change_sort)
        # Put frame in window
        frame.pack(padx=30, pady=30, expand=True, fill=tk.BOTH)

    # This function opens the file dialog window, gets the widget values, and calls the web scraping bot
    def create_csv(self):
        # File Dialog window
        save_path = fd.asksaveasfile(mode="w", initialfile="mod-data.csv", defaultextension=".csv")

        # Get widget values to make url search
        results = str(self.results.get())  # Get desired results quantity
        order = self.order.get()  # Ascending or Descending
        platform = self.platform_combobox.get()  # get console name
        game = self.game.get()  # Fallout 4 or Skyrim
        match self.sort_combobox.current():  # Get sort choice from list, display text differs from url text
            case 0:
                sort = "published"
            case 1:
                sort = "popular"
            case 2:
                sort = "rating"
            case 3:
                sort = "follow"
            case _:
                sort = "published"
        period = self.period_combobox.get()  # Get period choice from list
        search_term = self.search_entry.get()  # Get Search Term
        # Get categories selection as list
        selected_categories = [self.categories_listbox.get(i) for i in self.categories_listbox.curselection()]

        # Initiate Web Scraping Bot
        bot = BethesdaNetScraper(CHROME_DRIVER_PATH)
        bot.get_new_mods(save_path, results, order, platform, game, sort, period, search_term, selected_categories)

    # This function disables the time period option if the "Date" sorting method is selected.
    def change_sort(self, event):
        if self.sort_combobox.get() == "Date":
            self.period_combobox.config(state='disabled')
        else:
            self.period_combobox.config(state="normal")


root = tk.Tk()
root.title("Bethesda.net Web Scraper")
window = Window(root)
root.mainloop()
