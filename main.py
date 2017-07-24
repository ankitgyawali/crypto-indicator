#!/usr/bin/env python3
import signal
import gi
import os
from math import floor
import json
import urllib.request

from PIL import Image, ImageDraw, ImageFont

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GObject, Pango
import time
from threading import Thread

# coins = ['ETH','BTC','REP','GNT','IOTA','TRST','ANT','FUN']
coins = ['ETH','BTC','REP','GNT','BAT','ICN','RDD']
base_value = 'USD'
url = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=" + ",".join(coins) + "&tsyms=" + base_value


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
        create_a_header("Coin",  "     24hr +/- %", "   Price ("+base_value+")", menu)

        make_menus(get_prices(),menu)

        menu_item = Gtk.ImageMenuItem.new_with_label("Total Holdings: ")
        menu_item.set_always_show_image(True)
        menu.append(Gtk.SeparatorMenuItem())          
        menu.append(menu_item)
        menu_item.set_image(Gtk.Image.new_from_file(os.path.abspath("icons/USDT.svg")))

        # menu_item.set_image(Gtk.Image.new_from_file(os.path.abspath("icons/BTC-alt.svg")))
        # menu_item.set_image(Gtk.Image.new_from_file(img))
        
        # Label Markup width
        # row = Gtk.ImageMenuItem()
        # menu.append(row)
        # label = Gtk.Label('', xalign=0)
        # label.modify_font(Pango.FontDescription('monospace 18'))
        # label.set_markup("<span font_desc='unifont medium'>%s</span>" % 'ASTX')
        
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

def process_coin_price(coin_price):
    return (str(coin_price))
    # if(coin_price>1):
    #     lenx = (8 - int(len(str(coin_price).split("#")[0])))
    #     lenx = (8)
    #     # lenx = int(len(str(coin_price).split("#")[0])) - 8
    #     price_format = "%." + str(lenx) +"f"
    #     return str(price_format % coin_price)
    # else:
    #     return str("%.8f" % coin_price)

def make_menus(prices,menu):
    for key in prices['RAW']:
        coin_symbol = str(prices['RAW'][key][base_value]['FROMSYMBOL'])
        coin_price = process_coin_price(prices['DISPLAY'][key][base_value]['PRICE'])
        coin_change = process_coin_change((prices['RAW'][key][base_value]['PRICE'] - prices['RAW'][key][base_value]['OPEN24HOUR'])/prices['RAW'][key][base_value]['PRICE'])
        coin_change+= ' ' * (21 - len(coin_change))
        menu_string = column_normalizer(coin_symbol) + column_normalizer(coin_change) + column_normalizer(coin_price)
        menu_item = Gtk.ImageMenuItem.new_with_label(menu_string)
        menu_item.set_always_show_image(True)
        menu.append(menu_item)
        menu_item.set_image(Gtk.Image.new_from_file(os.path.abspath("icons/"+ coin_symbol +".svg")))

def create_a_menu(col1, col2, col3, menu):
    # col3+= "                     "
    col3+= ' ' * (21 - len(col3))
    # col2= ' ' * (5 - len(col2))
    menu_string = column_normalizer(col1) + column_normalizer(col2) + column_normalizer(col3)
    menu.append(Gtk.MenuItem(menu_string))
    menu.append(Gtk.SeparatorMenuItem())  

def create_a_header(col1, col2, col3, menu):
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