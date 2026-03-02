import requests
import urllib.parse

prompt = "A cute flat illustration of a cat programming"
encoded = urllib.parse.quote(prompt)

urls = [
    f"https://image.pollinations.ai/prompt/{encoded}",
    f"https://pollinations.ai/p/{encoded}",
]

for url in urls:
    try:
        resp = requests.get(url, timeout=10)
        print(f"URL: {url} -> Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Success! Content type: {resp.headers.get('content-type')}")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
