import json
import time
import os
import urllib.request
import requests
import shutil

# Time to sleep to avoid rate limit error
rate_limit_time = 3


# Local folder Structures
folder = "/icons/"
coin = []
name = []
url = "https://www.cryptocompare.com/api/data/coinlist/"

# Get initial coin list via API
data = json.loads(urllib.request.urlopen(urllib.request.Request(url)).read().decode('utf-8'))

# Loop through data to create list of coin names/coin image request url
for key in data['Data']:
    if 'ImageUrl' in data['Data'][key]:
        coin.append(url+ data['Data'][key]['ImageUrl'])
        name.append( data['Data'][key]['Name'])

# Check if coin image exists already
def check(icon_path):
    if os.path.isfile(icon_path):
        return True
    else:
        return False

total = str(len(coin))

# Loop through coin list, make request if they exist with rate limit in between
for index in range(len(coin)):
    icon_path = os.getcwd()+folder+ name[index] + ".png"
    if (check(icon_path)):
        print("["+ str(index+1) + "/"+ total +"]: File for " + name[index] +" exists already")
    else:
        print(coin[index])
        print("Sleeping " + str(rate_limit_time) +" seconds to avoid rate limit..")
        time.sleep(rate_limit_time)        
        response = requests.get(coin[index], stream=True)
        with open(icon_path,'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
            print("["+ str(index+1) + "/"+ total +"]: Saved: " + icon_path)
        del response