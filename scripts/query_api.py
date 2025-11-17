import urllib.request, json
u='http://127.0.0.1:8000/api/systems'
with urllib.request.urlopen(u) as r:
    data=json.load(r)
    print(type(data))
    print(list(data.keys())[:10])
    import pprint
    pprint.pprint(data)
