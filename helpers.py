import json
import urllib.request
from math import floor

# Converts list to a set and back to list while preserving order
def list_to_set_preserve_order(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

# Makes main call to crypto compare api
def get_prices(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url)).read().decode('utf-8'))

# Returns a single Indicator Label in format- $ Price (VAL/BASE)
def get_init_price(prices, val, base):
    return str(prices['DISPLAY'][val][base]['PRICE'])  + " (" + val + "/" + base + ")"

# Beautifies % changed to a readable format
def process_coin_change(coin_change):
    coin_change *= 10 ** (2 + 2)
    return_val = '{1:.{0}f}%'.format(2, floor(coin_change) / 10 ** 2)
    if (coin_change>0):
        return "+ "  +return_val
    else:
        return return_val.replace("-", "- ")

# Returns value of coins held
# TODO: Use Base val
def calculate_coin_holding(raw_price,number_of_coins):
    return float(raw_price) * float(number_of_coins)

# Control width of column in case monospace font is used
def column_normalizer(string):
    width = 25
    return (string + ' ' * (width - len(string)))

# Return the main header String 
def create_a_header(col1, col2, col3, display_holdings):
    if (display_holdings):
        return column_normalizer(col1) + column_normalizer(col2) + column_normalizer(col3) + column_normalizer("HOLDINGS")
    else:
        return column_normalizer(col1) + column_normalizer(col2) + column_normalizer(col3)
