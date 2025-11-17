import requests

URL = 'http://127.0.0.1:8000/api/save_system'

sample = {
    'name': 'UNITTEST SYS',
    'region': 'UNITTEST',
    'x': '1',
    'y': '2',
    'z': '10',
    'planets': [
        {'name': 'UT-Planet-1', 'sentinel': 'Low', 'moons': [{'name': 'UT-Moon-1'}]}
    ]
}

r = requests.post(URL, json=sample)
print(r.status_code)
print(r.text)
