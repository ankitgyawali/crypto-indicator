#!/usr/bin/env python3
import signal
import gi
import os

import json
import urllib.request


gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GObject
import time
from threading import Thread

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
        self.indicator.set_label("$"+get_prices()+"/ETH", self.app)
        # self.indicator.set_label("$"+get_prices()+"/ETH", self.app)
        # the thread:
        self.update = Thread(target=self.show_seconds)
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()



    def create_menu(self):
        menu = Gtk.Menu()
        # menu item 1
        create_a_header("Coin",  "24hr +/- %", "Price", menu)
        create_a_menu("ETH", "$101.2", "$2635.4", menu)
        create_a_menu("SCJ", "$1210.2", "$263445.4", menu)
        create_a_menu("SCJX", "$1210.2", "$263445.4", menu)

        menu.append(Gtk.ImageMenuItem("Total Holdings: "))
        menu_item = Gtk.ImageMenuItem.new_with_label("label")
        menu_item.set_always_show_image(True)
        menu.append(menu_item)
        menu_item.set_image(Gtk.Image.new_from_file(os.path.abspath("icons/SJCX.svg")))

        menu_item = Gtk.ImageMenuItem.new_with_label("label")
        menu_item.set_always_show_image(True)
        menu.append(menu_item)
        menu_item.set_image(Gtk.Image.new_from_file(os.path.abspath("icons/BTC-alt.svg")))


        # unmounted = Gtk.MenuItem('Unmounted Partitions')
        # unmounted_submenu = Gtk.Menu()
        # unmounted.set_submenu(unmounted_submenu)
        # menu.append(unmounted)
        
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
            mention = "$"+get_prices()+"/ETH"
            # apply the interface update using  GObject.idle_add()
            GObject.idle_add(
                self.indicator.set_label,
                mention, self.app,
               priority=GObject.PRIORITY_DEFAULT
                )

    def stop(self, source):
        Gtk.main_quit()
      
    
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


def get_prices():
    url = "https://api.coinmarketcap.com/v1/ticker/ethereum/?convert=USD"
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    eth = json.loads(response.read().decode('utf-8'))[0]['price_usd']
    eth = str(eth)
    return eth

Indicator()
# this is where we call GObject.threads_init()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()