import requests

url = 'https://api.kukuit.com/v1/chat/completions'
headers = {
    'Authorization': 'Bearer sk-imx79wtX4EMh7AdwCtPwWOYhnyYBBVlEzRQlvYnDUjpPh601',
    'Content-Type': 'application/json',
}
payload = {
    'model': 'deepseek-v4-flash',
    'messages': [
        {'role': 'user', 'content': '返回一个简单的JSON: {"test": 1}'}
    ],
}

resp = requests.post(url, headers=headers, json=payload)
text = resp.text
print('Raw response:', repr(text[:200]))
print('Length:', len(text))

try:
    import json
    data = json.loads(text)
    print('JSON parsed successfully')
    print('Content:', data)
except Exception as e:
    print('JSON parse error:', e)
