import re

query = "create a well with name LORA OIL, depth 3000, Status DHELLA"
query_lower = query.lower()

print(f"Query: {query_lower}")

# Robust pattern using non-greedy matching
pattern0 = r"(?:create|insert|add).*?name\s+([^,]+).*?depth\s+(\d+).*?status\s+(\w+)"
match0 = re.search(pattern0, query_lower)

if match0:
    print("Pattern 0 MATCHED!")
    print(f"Name: {match0.group(1)}")
    print(f"Depth: {match0.group(2)}")
    print(f"Status: {match0.group(3)}")
else:
    print("Pattern 0 FAILED")

# Pattern 0a (Simple Create)
pattern0a = r"(?:create|insert|add)(?:\s+new)?\s+well\s+(?:with\s+name\s+|named\s+)?(.+)"
match0a = re.search(pattern0a, query_lower)

if match0a:
    print("Pattern 0a MATCHED!")
    well_name = match0a.group(1).strip()
    print(f"Raw captured name: '{well_name}'")
    
    # Simulate cleanup
    well_name_clean = re.sub(r'\s+(with|and|at).*$', '', well_name)
    print(f"Cleaned name: '{well_name_clean}'")
    
    if ',' in well_name_clean:
        print("Comma detected -> Skip Pattern 0a")
    else:
        print("No comma -> Pattern 0a SUCCESS (Simple Create)")
