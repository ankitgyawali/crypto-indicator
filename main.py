#!/usr/bin/env python3
import signal
import gi
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


config = configparser.ConfigParser()
config.readfp(open(r'config.ini'))

coins = json.loads(config.get('INDICATOR_OPTIONS', 'COINS_TO_SHOW'))

display_holdings = (config.get('INDICATOR_OPTIONS', 'DISPLAY_HOLDINGS') == '1')

primary_coins = json.loads(config.get('INDICATOR_OPTIONS', 'COINS_TO_SHOW'))

base_coins = []
base_coins.append(config.get('INDICATOR_OPTIONS', 'COINS_BASE_VALUE'))

holding_coins = []
holding_vals = []

silent_holding_coins = []
silent_holding_vals = []


total_holdings = 0


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

# secondary_coins = config.items('INDICATOR_LABELS')

# coins = ['ETH','BTC','REP','GNT','BAT','ICN','CFI','SYS','LSK']
base_value = 'USD'
display_indicator = [['ETH', 'USD'], ['ETH','BTC']]

url = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=" + ",".join(primary_coins) + "&tsyms=" +  ",".join(base_coins)

class Indicator():
    def __init__(self):
        self.app = 'crypto-indicator'
        iconpath = os.path.abspath("indicator-icon.svg")
        self.indicator = AppIndicator3.Indicator.new(
            self.app, iconpath,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.indicator.set_menu(self.create_menu())
        # Dev only
        self.indicator.set_label("$"+get_init_price(get_prices())+"/ETH", self.app)
        # self.indicator.set_label("$"+get_prices()+"/ETH", self.app)
        # the thread:
        self.update = Thread(target=self.show_seconds)
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()



    def create_menu(self):
        menu = Gtk.Menu()
        # menu item 1
        create_a_header("Coin",  "     24hr +/- %", "   Price ("+base_value+")", display_holdings, menu)

        make_menus(get_prices(),display_holdings, coins_to_show, holding_coins, holding_vals, menu)

        menu_item = Gtk.MenuItem.new_with_label("Total Holdings: "+ str(display_holdings))
        # menu_item.set_always_show_image(True)
        menu.append(Gtk.SeparatorMenuItem())          
        menu.append(menu_item)
        
        configure_app = Gtk.MenuItem.new_with_label("Configure")
        # menu_item.set_always_show_image(True)
        menu.append(Gtk.SeparatorMenuItem())          
        menu.append(configure_app)
        
        # label.set_max_width_chars(3)
        # row.add(label)

        # IMAGE
        # menu.append(Gtk.MenuItem("ETHX --- $101.2 ---  $2635.4 --- 12 --- $265.4"))
        menu.append(Gtk.SeparatorMenuItem())  

        # item_about.connect('activate', self.about)
        # separator
        menu.append(Gtk.SeparatorMenuItem())
        # quit
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.stop)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def show_seconds(self):
        while True:
            time.sleep(60)
            mention = "$"+get_init_price(get_prices())+"/ETH"
            # apply the interface update using  GObject.idle_add()
            GObject.idle_add(
                self.indicator.set_label,
                mention, self.app,
               priority=GObject.PRIORITY_DEFAULT
                )

    def stop(self, source):
        Gtk.main_quit()



def process_coin_change(coin_change):
    coin_change *= 10 ** (2 + 2)
    return_val = '{1:.{0}f}%'.format(2, floor(coin_change) / 10 ** 2)
    if (coin_change>0):
        return "+ "  +return_val
    else:
        return return_val.replace("-", "- ")

def calculate_coin_holding(raw_price,number_of_coins,total_holdings):
    return str(raw_price) + str(number_of_coins) + str(total_holdings)

def make_menus(prices, display_holdings, coins_to_show, holding_coins, holding_vals, menu):
    for coin in coins_to_show:
        coin_symbol = str(prices['RAW'][coin][base_value]['FROMSYMBOL'])
        coin_price = prices['DISPLAY'][coin][base_value]['PRICE']
        coin_change = process_coin_change((prices['RAW'][coin][base_value]['PRICE'] - prices['RAW'][coin][base_value]['OPEN24HOUR'])/prices['RAW'][coin][base_value]['PRICE'])
        coin_change+= ' ' * (21 - len(coin_change))
        menu_string = column_normalizer(coin_symbol) + column_normalizer(coin_change) + column_normalizer(coin_price)
        if (display_holdings and (coin in holding_coins)):
            menu_string += calculate_coin_holding(prices['DISPLAY'][coin][base_value]['PRICE'], holding_vals[holding_coins.index(coin)] ,total_holdings)
        menu_item = Gtk.ImageMenuItem.new_with_label(menu_string)
        menu_item.set_always_show_image(True)
        menu.append(menu_item)
        menu_item.set_image(Gtk.Image.new_from_file(os.path.abspath("icons/"+ coin_symbol +".png")))

    # for key in prices['RAW']:
    #     coin_symbol = str(prices['RAW'][key][base_value]['FROMSYMBOL'])
    #     coin_price = prices['DISPLAY'][key][base_value]['PRICE']
    #     coin_change = process_coin_change((prices['RAW'][key][base_value]['PRICE'] - prices['RAW'][key][base_value]['OPEN24HOUR'])/prices['RAW'][key][base_value]['PRICE'])
    #     coin_change+= ' ' * (21 - len(coin_change))
    #     if (display_holdings):
    #         menu_string = column_normalizer(coin_symbol) + column_normalizer(coin_change) + column_normalizer(coin_price) + "$100.00"
    #     else:
    #         menu_string = column_normalizer(coin_symbol) + column_normalizer(coin_change) + column_normalizer(coin_price)            
    #     menu_item = Gtk.ImageMenuItem.new_with_label(menu_string)
    #     menu_item.set_always_show_image(True)
    #     menu.append(menu_item)
    #     menu_item.set_image(Gtk.Image.new_from_file(os.path.abspath("icons/"+ coin_symbol +".png")))

#############################################################


# def create_a_menu(col1, col2, col3, menu):
#     # col3+= "                     "
#     col3+= ' ' * (21 - len(col3))
#     # col2= ' ' * (5 - len(col2))
#     menu_string = column_normalizer(col1) + column_normalizer(col2) + column_normalizer(col3)
#     menu.append(Gtk.MenuItem(menu_string))
#     menu.append(Gtk.SeparatorMenuItem())  

def create_a_header(col1, col2, col3, display_holdings, menu):
    if (display_holdings):
        menu_string = column_normalizer(col1) + column_normalizer(col2) + column_normalizer(col3) + column_normalizer("HOLDINGS")
    else:
        menu_string = column_normalizer(col1) + column_normalizer(col2) + column_normalizer(col3)
    menu.append(Gtk.MenuItem(menu_string))
    # menu.append(Gtk.MenuItem("ETHX --- $101.2 ---  $2635.4 --- 12 --- $265.4"))
    menu.append(Gtk.SeparatorMenuItem())  

def column_normalizer(string):
    width = 25
    return (string + ' ' * (width - len(string)))

def get_init_price(prices):
    return str(prices['RAW']['ETH'][base_value]['PRICE'])

def get_prices():
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    dump = json.loads(response.read().decode('utf-8'))
    eth = dump['RAW']['ETH'][base_value]['PRICE']
    return dump

Indicator()
# this is where we call GObject.threads_init()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()