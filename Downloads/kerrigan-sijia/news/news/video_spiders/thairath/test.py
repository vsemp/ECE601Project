import re
import requests
r = requests.get('https://www.thairath.co.th/clip/140703')
print (r.text)
