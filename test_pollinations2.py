import requests
import urllib.parse

prompt = "cat"
encoded = urllib.parse.quote(prompt)

urls = [
    f"https://pollinations.ai/prompt/{encoded}",
    f"https://image.pollinations.ai/prompt/{encoded}",
]

for url in urls:
    try:
        resp = requests.get(url, timeout=10)
        print(f"URL: {url} -> Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type')}")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
