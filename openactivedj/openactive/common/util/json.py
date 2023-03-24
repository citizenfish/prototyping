import requests
from functools import reduce
from bs4 import BeautifulSoup as bs
import json

def get_json(url, path=None):
    # path = "foo.baaa.wibble"
    try:
        res = requests.get(url)
        json = res.json()
        if json and path:
            ret = reduce(lambda acc, i: acc[i], path.split('.'), json)
            return ret
        if json:
            return json
    except Exception as error:
        print(f"getJson error: {str(error)} path: {path}")
        return {}

def get_json_ld(url):
    # This returns the body of a json_LD script from openActive api

    try:

        html = requests.get(url).content
        soup = bs(html, "html.parser")
        for script in soup.find_all("script"):
            type = script.attrs.get("type", '')
            if type != '' and type == 'application/ld+json':
                return json.loads(script.text)
        return {}
    except Exception as error:
        print(str(error))
        return {}
