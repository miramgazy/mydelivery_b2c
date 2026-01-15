import json

try:
    with open('/Users/miramgazy/Library/Mobile Documents/com~apple~CloudDocs/Progects/tg-delivery/downloaded_menu.json', 'r') as f:
        data = json.load(f)
    
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
        
    products = data.get('products', [])
    if products:
        print(json.dumps(products[0], indent=2, ensure_ascii=False))
        
        # Count types
        types = {}
        for p in products:
            t = p.get('type')
            types[t] = types.get(t, 0) + 1
        print("\nTypes distribution:")
        print(types)
        
except Exception as e:
    print(f"Error: {e}")
