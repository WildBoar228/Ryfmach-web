import requests
import time
import json


for i in range(100):
    t1 = time.time()
    answer = requests.post("https://inaudibly-consistent-mullet.cloudpub.ru/",
                           json={"word": "каралі"})
    print(f"Got answer (len = {answer.json}), {round(time.time() - t1, 4)}s")
