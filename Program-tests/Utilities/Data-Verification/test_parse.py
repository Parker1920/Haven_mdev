location_info = None
print('Input:', location_info)
try:
    parts = location_info.split(':', 2)
    print('Parts:', parts)
except AttributeError as e:
    print('Error:', e)
