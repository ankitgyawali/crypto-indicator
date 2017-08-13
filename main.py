#!/usr/bin/env python3
import signal
import gi
import webbrowser
import os
from math import floor
import json
import urllib.request
import configparser
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GObject, Pango
import time
from threading import Thread
import subprocess


config = configparser.ConfigParser()
config.readfp(open(r'config.ini'))

coins = json.loads(config.get('INDICATOR_OPTIONS', 'COINS_TO_SHOW'))

display_holdings = (config.get('INDICATOR_OPTIONS', 'DISPLAY_HOLDINGS_IN_MENU') == '1')
display_holdings_label = (config.get('INDICATOR_LABELS', 'DISPLAY_TOTAL_HOLDINGS_IN_INDICATOR_LABEL') == '1')

primary_coins = json.loads(config.get('INDICATOR_OPTIONS', 'COINS_TO_SHOW'))

base_coins = []
base_coins.append(config.get('INDICATOR_OPTIONS', 'COINS_BASE_VALUE'))

holding_coins = []
holding_vals = []

silent_holding_coins = []
silent_holding_vals = []


for main_pair in json.loads(config.get('INDICATOR_LABELS', 'PAIRS')):
    primary_coins.append(main_pair[0].upper())
    base_coins.append(main_pair[1].upper())

for holdings_pair in config.items('HOLDINGS'):
    primary_coins.append(holdings_pair[0].upper())
    holding_coins.append(holdings_pair[0].upper())
    holding_vals.append(holdings_pair[1])

# Show everything on this list. Check before displaying the ones on silent holdings
coins_to_show = list(primary_coins)

for silent_holdings_pair in config.items('SILENT_HOLDINGS'):
    primary_coins.append(silent_holdings_pair[0].upper())
    silent_holding_coins.append(silent_holdings_pair[0].upper())
    silent_holding_vals.append(silent_holdings_pair[1])

def list_to_set_preserve_order(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

primary_coins = list_to_set_preserve_order(primary_coins)
base_coins = list_to_set_preserve_order(base_coins)
coins_to_show = list_to_set_preserve_order(coins_to_show)
base_value = config.get('INDICATOR_OPTIONS', 'COINS_BASE_VALUE').replace("\"","").replace("'","")
display_indicator = [['ETH', 'USD'], ['ETH','BTC']]

url = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=" + ",".join(primary_coins) + "&tsyms=" +  ",".join(base_coins) + "," + base_value

def get_prices():
    return json.loads(urllib.request.urlopen(urllib.request.Request(url)).read().decode('utf-8'))

prices = get_prices()

def get_init_price(prices, val, base):
    return str(prices['DISPLAY'][val][base]['PRICE'])  + " (" + val + "/" + base + ")"

main_symbol = str(prices['DISPLAY'][str((list(prices['DISPLAY'].keys())[0]))][base_value]['PRICE'])
main_symbol = ''.join(i for i in main_symbol if not i.isdigit()).replace(".","").replace(",","").strip()

separator = " " + (config.get('INDICATOR_LABELS', 'SEPARATOR_SYMBOL')).replace("\"","").replace("'","")+ " "
initial_display_string = ''

each_label = []
for label in json.loads(config.get('INDICATOR_LABELS', 'PAIRS')):
    each_label.append(get_init_price(prices,label[0],label[1]))
initial_display_string =  separator.join(each_label) 

def process_coin_change(coin_change):
    coin_change *= 10 ** (2 + 2)
    return_val = '{1:.{0}f}%'.format(2, floor(coin_change) / 10 ** 2)
    if (coin_change>0):
        return "+ "  +return_val
    else:
        return return_val.replace("-", "- ")

# TODO: Add Holdings according to base price
def calculate_coin_holding(raw_price,number_of_coins):
    return float(raw_price) * float(number_of_coins)
    
def column_normalizer(string):
    width = 25
    return (string + ' ' * (width - len(string)))

class Indicator():
    def __init__(self):
        self.app = 'crypto-indicator'
        iconpath = os.path.abspath("indicator-icon.svg")
        self.indicator = AppIndicator3.Indicator.new(
            self.app, iconpath,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.sub_menus = self.create_menu()
        self.indicator.set_menu(self.sub_menus)
        # the thread:
        self.update = Thread(target=self.update_indicator)
        
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()

    def open_file(self, *args):
        webbrowser.open('https://www.github.com/ankitgyawali', new=2)    
        subprocess.call(["xdg-open", os.path.abspath("config.ini")])

    def about(self, *args):
        window = Gtk.Window()
        window.set_border_width(20)
        vert = Gtk.Orientation.VERTICAL
        horz = Gtk.Orientation.HORIZONTAL
        main_box = Gtk.Box(orientation=vert, spacing=5)
        listbox = Gtk.ListBoxRow()
        main_box.pack_start(listbox, True, True, 0)
        label = Gtk.Label()
        # label = Gtk.Label("This is an example of a line")
        label.set_markup("Configure your coins on the following ini file with your favourite text editor. \n ~/.config/crypto-indicator-config.ini \n \n Instructions provided on the .ini file.\n More detailed instructions provided on <a href='https://www.github.com/ankitgyawali'>https://www.github.com/ankitgyawali</a>")
        label.set_selectable(True)
        main_box.add(label)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.add(main_box)
        # window.add(e)
        # e.grab_focus()
        window.show_all()
        gtk.Window.present()

    def create_menu(self):
        self.menu = Gtk.Menu()
        # menu item 1
        create_a_header("Coin",  "     24hr +/- %", "   Price ("+base_value+")", display_holdings, self.menu)

        holdings_val = make_menus(prices,display_holdings, coins_to_show, holding_coins, holding_vals,silent_holding_coins, silent_holding_vals, self.menu, self)
        holdings = " $" + ("%.2f" % (sum(holdings_val)))
        self.total_holdings_item = Gtk.MenuItem.new_with_label("Total Holdings: " + holdings)

        ## Update label 
        holdings_label = ''
        if(display_holdings_label):
            holdings_label = " " + separator + "Holdings: " + holdings

        self.indicator.set_label(initial_display_string + holdings_label, self.app)
        
        self.menu.append(Gtk.SeparatorMenuItem())          
        self.menu.append(self.total_holdings_item)
        self.menu.append(Gtk.SeparatorMenuItem())          

        about = Gtk.MenuItem('Configure')
        self.menu.append(about)
        about.connect('activate', self.about)
        
        config_indicator = Gtk.MenuItem('About')
        self.menu.append(config_indicator)
        # config_indicator.connect('activate', self.open_file)
        config_indicator.connect("activate", self.open_file)        

        # quit
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.stop)
        self.menu.append(item_quit)
        # self.indicator.set_label("AA",self.app)
        self.menu.show_all()
        return self.menu

    def update_indicator(self):
        a= 1
        while True:
            
            time.sleep(int(config.get('INDICATOR_OPTIONS', 'REFRESH_TIME_IN_SECONDS')))

            separator = " " + (config.get('INDICATOR_LABELS', 'SEPARATOR_SYMBOL')).replace("\"","").replace("'","")+ " "
            initial_display_string = ''

            each_label = []
            prices = get_prices()            
            for label in json.loads(config.get('INDICATOR_LABELS', 'PAIRS')):
                each_label.append(get_init_price(prices,label[0],label[1]))
            initial_display_string =  separator.join(each_label)

            all_holdings = []
            for silent_coin in silent_holding_coins:
                all_holdings.append(calculate_coin_holding(prices['RAW'][silent_coin][base_value]['PRICE'], silent_holding_vals[silent_holding_coins.index(silent_coin)].replace(",","")))

            ###########
            for idx, coin in enumerate(self.coin_names):
                coin_symbol = str(prices['RAW'][coin][base_value]['FROMSYMBOL'])
                coin_price = prices['DISPLAY'][coin][base_value]['PRICE']
                coin_change = process_coin_change((prices['RAW'][coin][base_value]['PRICE'] - prices['RAW'][coin][base_value]['OPEN24HOUR'])/prices['RAW'][coin][base_value]['PRICE'])
                coin_change+= ' ' * (21 - len(coin_change))
                menu_string = column_normalizer(coin_symbol) + column_normalizer(coin_change) + column_normalizer(coin_price)
                if (display_holdings and (coin in holding_coins)): # This condition checks for holdings that are also shown
                    all_holdings.append(calculate_coin_holding(prices['RAW'][coin][base_value]['PRICE'], holding_vals[holding_coins.index(coin)].replace(",","")))
                    menu_string += "$" + ("%.4f" % calculate_coin_holding(prices['RAW'][coin][base_value]['PRICE'], holding_vals[holding_coins.index(coin)].replace(",","")))
                GObject.idle_add(self.coin_menu_rows[idx].set_label, str(menu_string))

            holdings = " $" + ("%.2f" % (sum(all_holdings)))
            GObject.idle_add(self.total_holdings_item.set_label, "Total Holdings: " + holdings)

            holdings_label = ''
            if(display_holdings_label):
                holdings_label = " " + separator + "Holdings: " + holdings

            GObject.idle_add(self.indicator.set_label, initial_display_string + holdings_label, self.app, priority=GObject.PRIORITY_DEFAULT)

    def stop(self, source):
        Gtk.main_quit()

def make_menus(prices, display_holdings, coins_to_show, holding_coins, holding_vals, silent_holding_coins, silent_holding_vals, menu, self):
    self.coin_menu_rows = []
    self.coin_names = []
    all_holdings = []
    # Calculate silent holding prices
    for silent_coin in silent_holding_coins:
        all_holdings.append(calculate_coin_holding(prices['RAW'][silent_coin][base_value]['PRICE'], silent_holding_vals[silent_holding_coins.index(silent_coin)].replace(",","")))
    for coin in coins_to_show:
        coin_symbol = str(prices['RAW'][coin][base_value]['FROMSYMBOL'])
        coin_price = prices['DISPLAY'][coin][base_value]['PRICE']
        coin_change = process_coin_change((prices['RAW'][coin][base_value]['PRICE'] - prices['RAW'][coin][base_value]['OPEN24HOUR'])/prices['RAW'][coin][base_value]['PRICE'])
        coin_change+= ' ' * (21 - len(coin_change))
        menu_string = column_normalizer(coin_symbol) + column_normalizer(coin_change) + column_normalizer(coin_price)
        if (display_holdings and (coin in holding_coins)): # This condition checks for holdings that are also shown
            all_holdings.append(calculate_coin_holding(prices['RAW'][coin][base_value]['PRICE'], holding_vals[holding_coins.index(coin)].replace(",","")))
            menu_string += "$" + ("%.4f" % calculate_coin_holding(prices['RAW'][coin][base_value]['PRICE'], holding_vals[holding_coins.index(coin)].replace(",","")))
        self.coin_names.append(coin)
        # MENU LABEL
        self.coin_menu_rows.append(Gtk.ImageMenuItem.new_with_label(menu_string))
        self.coin_menu_rows[-1].set_always_show_image(True)
        self.coin_menu_rows[-1].set_image(Gtk.Image.new_from_file(os.path.abspath("icons/"+ coin_symbol +".png")))
        menu.append(self.coin_menu_rows[-1])
        # menu.append(menu_item)
    return all_holdings

def create_a_header(col1, col2, col3, display_holdings, menu):
    if (display_holdings):
        menu_string = column_normalizer(col1) + column_normalizer(col2) + column_normalizer(col3) + column_normalizer("HOLDINGS")
    else:
        menu_string = column_normalizer(col1) + column_normalizer(col2) + column_normalizer(col3)
    menu.append(Gtk.MenuItem(menu_string))
    menu.append(Gtk.SeparatorMenuItem())  

## Try opening on init
subprocess.Popen(["xdg-open", os.path.abspath("config.ini")])

Indicator()
# this is where we call GObject.threads_init()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()