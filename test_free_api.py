import requests
import urllib.parse

prompt = "A cute flat illustration of a cat programming"
encoded = urllib.parse.quote(prompt)

urls = [
    f"https://api.airforce/imagine?prompt={encoded}",
    f"https://api.airforce/v1/imagine2?prompt={encoded}",
    f"https://api.airforce/v1/imagine?prompt={encoded}"
]

for url in urls:
    try:
        resp = requests.get(url, timeout=10)
        print(f"URL: {url} -> Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type')}")
        if resp.status_code == 200:
            print("Success!")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
