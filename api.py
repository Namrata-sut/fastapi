import requests

response = requests.get('https://coralvanda.github.io/pokemon_data.json')
print(response.status_code)
print(response.json())