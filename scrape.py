import json
import time
import os
import urllib.request
import requests
import shutil


folder = "/icons/"
coin = []
name = []
url = "https://cryptocompare.com"

# via API
request = urllib.request.Request("https://www.cryptocompare.com/api/data/coinlist/")
response = urllib.request.urlopen(request)
data = json.loads(response.read().decode('utf-8'))


for key in data['Data']:
    if 'ImageUrl' in data['Data'][key]:
        coin.append(url+ data['Data'][key]['ImageUrl'])
        name.append( data['Data'][key]['Name'])

def check(icon_path):
    if os.path.isfile(icon_path):
        return True
    else:
        return False

total = str(len(coin))

for index in range(len(coin)):
    icon_path = os.getcwd()+folder+ name[index] + ".png"
    if (check(icon_path)):
        print("["+ str(index+1) + "/"+ total +"]: File for " + name[index] +" exists already")
    else:
        print(coin[index])
        time.sleep(11)        
        response = requests.get(coin[index], stream=True)
        with open(icon_path,'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
            print("["+ str(index+1) + "/"+ total +"]: Saved: " + icon_path)
        del response
