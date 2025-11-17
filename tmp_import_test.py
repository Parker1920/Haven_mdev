import importlib, traceback, sys
print('Python executable:', sys.executable)
print('\nsys.path (first 10 entries):')
for p in sys.path[:10]:
    print('  ', p)
print('\nAttempting to import src.control_room_api...')
try:
    m = importlib.import_module('src.control_room_api')
    print('\nImported src.control_room_api OK:', m)
except Exception:
    traceback.print_exc()
