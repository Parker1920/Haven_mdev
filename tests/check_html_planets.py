#!/usr/bin/env python3
import re
import json

html_file = "dist/system_LEPUSCAR_OMEGA.html"
content = open(html_file, encoding='utf-8').read()

# Find SYSTEMS_DATA value
match = re.search(r'window\.SYSTEMS_DATA = (\[.*?\]);', content, re.DOTALL)
if match:
    json_str = match.group(1)
    # Truncate to first 1000 chars for readability
    if len(json_str) > 1500:
        print(json_str[:1500] + "...[truncated]")
    else:
        print(json_str)
else:
    print("SYSTEMS_DATA not found in HTML")
