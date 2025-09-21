import json

print("🕵️  Checking data.json for bugs...")

try:
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    bug_found = False

    # Check the 'skills' dictionary for an empty key
    if "skills" in data:
        for key in data["skills"].keys():
            if key == "":
                print("\n🔴 BUG FOUND in 'skills' section!")
                print(f'   There is an empty key "" with the value: "{data["skills"][key]}"')
                bug_found = True

    # Check the 'categories' dictionary for an empty key
    if "categories" in data:
        for key in data["categories"].keys():
            if key == "":
                print("\n🔴 BUG FOUND in 'categories' section!")
                print(f'   There is an empty key "" with the value: "{data["categories"][key]}"')
                bug_found = True

    if not bug_found:
        print("\n✅ No empty keys found. Your data.json structure looks correct!")

except FileNotFoundError:
    print("\n❌ ERROR: Could not find data.json in this folder.")
except json.JSONDecodeError:
    print("\n❌ ERROR: data.json has a syntax error (like a missing comma) and cannot be read.")