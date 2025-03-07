import requests

response = {'ipaddress': '', 'location': '', 'isp': '', 'countrycode': ''}
try:
    request = requests.get('https://wtfismyip.com/json').json()
    response = {
        'ipaddress': request['YourFuckingIPAddress'],
        'location': request['YourFuckingLocation'],
        'isp': request['YourFuckingISP'],
        'countrycode': request['YourFuckingCountryCode'],
    }
    print(response)
except:
    pass