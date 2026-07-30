import requests

request = requests.get("https://api.beatleader.com/player/ryleeeee").json()
print (request["badges"][0]["player"]["name"])