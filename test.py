import time
import datetime
import re
import requests
from util import get_theft_time_list
"""
now = datetime.datetime.now()
print(now)
time.sleep(1)
print("sec delta", (datetime.datetime.now()-now).total_seconds())
"""

delta = datetime.timedelta(seconds=50)
now = datetime.datetime.now().replace(microsecond=0)

print(now)
print(now - delta)

if now > now - delta:
    print("right")
print("=================================")
parent_url = "http://localhost:8080/stocklist"


new_timestamps = []

try:
    response = requests.get(parent_url)
    if (response.status_code != 200):
        print("failed to send data")
    else:
        datas = response.json()
        print(datas)

except:
    print("Cannot connect to Server!")

print("=================================")
files = get_theft_time_list()
print(files)

datas = ['null', '2023-05-10 22:16:33', '2023-05-11 22:16:33']

for d in datas:
    if d == "null":
        continue
    if d not in files:
        new_timestamps.append(d)

print("new stamps:", new_timestamps)

theft_time = datetime.datetime.now().replace(microsecond=0)
print(theft_time)





