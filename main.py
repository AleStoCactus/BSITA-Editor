import requests
ciao=requests.get(
    "https://scoresaber.com/api/v2/players/76561198815073446/profile"
)

ciao2=ciao.json()

print(ciao2["player"]["playerNameInGame"])

