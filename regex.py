#!/usr/bin/env python3

import re
import json

def main():
    with open("free-ranks.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Regex to capture the full JSON blob from the Apple key
    pattern = (
        r'"\.v1\.catalog\.us\.charts\.types\.apps\.platform\.iphone\.genre\.'
        r'6007\.chart\.top-free\.limit\.100\.sparselimit\.100\.l\.en-us":'
        r'"(\{.*?\})"'
    )
    match = re.search(pattern, content, flags=re.DOTALL)
    if not match:
        print("Could not find the big JSON blob for the 'apps' array.")
        return

    # 2. Extract the raw JSON string from the match
    raw_json_str = match.group(1)

    # 3. Unescape quotes and common escaped characters
    unescaped_json = (
        raw_json_str
        .replace('\\"', '"')    # unescape quote
        .replace("\\n", "\n")   # unescape newline
        .replace("\\r", "\r")   # unescape carriage return
        .replace("\\t", "\t")   # unescape tab
    )

    # 4. Parse into a Python dictionary
    try:
        parsed = json.loads(unescaped_json)
    except json.JSONDecodeError as e:
        print("JSON parsing failed. Error:", e)
        return

    # 5. "apps" array is typically at: parsed["d"]["apps"]
    apps_section = parsed.get("d", {}).get("apps", [])
    if not apps_section:
        print("No 'apps' array found in the parsed JSON structure.")
        return

    # 6. We'll collect all 'apps' objects in a list
    all_apps = []

    # Each item in apps_section is usually a "chart" object
    for chart_item in apps_section:
        # The actual apps are within this object's "data" list
        data_items = chart_item.get("data", [])
        for item in data_items:
            if item.get("type") == "apps":
                # This dictionary (item) contains all keys/values for the app
                all_apps.append(item)

    # 7. Write all apps (with their keys/values) to a JSON file
    with open("all_apps.json", "w", encoding="utf-8") as out_f:
        json.dump(all_apps, out_f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(all_apps)} apps. See 'all_apps.json' for full details.")

if __name__ == "__main__":
    main()
