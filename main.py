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
import subprocess

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

def open_config():
    # index = self.menu.get_children().index(self.menu.get_active())
    # selection = self.menu_items2[index]
    # subprocess.Popen(["xdg-open", os.path.abspath("config.ini")])
    # os.system('xdg-open config.ini')
    subprocess.call(['xdg-open', os.path.abspath("config.ini")])

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
        # Dev only
        self.indicator.set_label("$"+get_init_price(get_prices())+"/ETH", self.app)
        # self.indicator.set_label("$"+get_prices()+"/ETH", self.app)
        # the thread:
        self.update = Thread(target=self.update_indicator)
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()

    def open_file(self, *args):
        # index = self.menu.get_children().index(self.menu.get_active())
        # selection = self.menu_items2[index]
        # subprocess.Popen(["xdg-open", os.path.abspath("config.ini")])
        # os.system('xdg-open config.ini')
        print("X")
        subprocess.call(['xdg-open', os.path.abspath("config.ini")])



    def create_menu(self):
        self.menu = Gtk.Menu()
        # menu item 1
        create_a_header("Coin",  "     24hr +/- %", "   Price ("+base_value+")", display_holdings, self.menu)

        holdings_val = make_menus(get_prices(),display_holdings, coins_to_show, holding_coins, holding_vals,silent_holding_coins, silent_holding_vals, self.menu, self)

        holdings = " $" + ("%.4f" % (sum(holdings_val)))


        # menu_item = Gtk.MenuItem.new_with_label("Total Holdings: " + holdings)
        menu_item = Gtk.MenuItem.new_with_label("Total Holdings: " + holdings)
        # menu_item.set_always_show_image(True)

        self.menu.append(Gtk.SeparatorMenuItem())          
        self.menu.append(menu_item)
        # "$" + ("%.4f" % d)
        import sys
        # sys.stdout("d")

        self.configure_app = Gtk.MenuItem.new_with_label("Configure")
        self.configure_app.set_label("Configure set label")

        sub = Gtk.MenuItem('config.ini')
        sub.connect('event', self.open_file)        
        self.menu.append(sub)
        # sub.connect('activate', open_config)


        # configure_app = Gtk.MenuItem.set_label("Configure",self.app)
        # menu_item.set_always_show_image(True)

        # configure_app.set_text("X")
        
        
        self.menu.append(Gtk.SeparatorMenuItem())          
        self.menu.append(self.configure_app)
        
        # label.set_max_width_chars(3)
        # row.add(label)

        # IMAGE
        # menu.append(Gtk.MenuItem("ETHX --- $101.2 ---  $2635.4 --- 12 --- $265.4"))
        self.menu.append(Gtk.SeparatorMenuItem())  

        # item_about.connect('activate', self.about)
        # separator
        self.menu.append(Gtk.SeparatorMenuItem())
        # quit
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.stop)
        self.menu.append(item_quit)

        self.menu.show_all()
        return self.menu

    def update_indicator(self):
        a= 1
        while True:
            time.sleep(int(config.get('INDICATOR_OPTIONS', 'REFRESH_TIME_IN_SECONDS')))


            new_prices = get_prices()
            new_label = "$"+get_init_price(new_prices)+"/ETH"
            GObject.idle_add(
                self.indicator.set_label, new_label, self.app,
               priority=GObject.PRIORITY_DEFAULT
                )


            # UPDATE GOES HERE
            # label = "Configure set:" + str(randint(0, 1000))

            GObject.idle_add(self.configure_app.set_label, new_label)



            # GObject.idle_add(
            #     self.configure_app.set_label,
            #     "Configure updated label", self.app,
            #    priority=GObject.PRIORITY_DEFAULT
            #     )

    def stop(self, source):
        Gtk.main_quit()

def process_coin_change(coin_change):
    coin_change *= 10 ** (2 + 2)
    return_val = '{1:.{0}f}%'.format(2, floor(coin_change) / 10 ** 2)
    if (coin_change>0):
        return "+ "  +return_val
    else:
        return return_val.replace("-", "- ")

# TODO: Add Holdings according to base price
def calculate_coin_holding(raw_price,number_of_coins):
    # total_holdings = total_holdings + (float(raw_price) * float(number_of_coins))
    # total_holdings += (float(raw_price) * float(number_of_coins))
    # return str((float(raw_price) * float(number_of_coins)))
    d =  float((float(raw_price) * float(number_of_coins)))
    return d
    # return "$" + ("%.4f" % d)

def make_menus(prices, display_holdings, coins_to_show, holding_coins, holding_vals, silent_holding_coins, silent_holding_vals, menu, self):
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
        
        
        # MENU LABEL
        menu_item = Gtk.ImageMenuItem.new_with_label(menu_string)
        
        menu_item.set_always_show_image(True)
        menu.append(menu_item)
        menu_item.set_image(Gtk.Image.new_from_file(os.path.abspath("icons/"+ coin_symbol +".png")))
    return all_holdings


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