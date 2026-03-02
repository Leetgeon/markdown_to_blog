import requests
import urllib.parse
from PIL import Image
import io

prompt = "A cute flat illustration of a cat programming"
encoded = urllib.parse.quote(prompt)

urls = [
    f"https://api.airforce/v1/imagine2?prompt={encoded}",
    f"https://pollinations.ai/p/{encoded}",
]

for url in urls:
    try:
        resp = requests.get(url, timeout=15)
        print(f"URL: {url} -> Content-Type: {resp.headers.get('content-type')}")
        if 'image' in resp.headers.get('content-type', ''):
            img = Image.open(io.BytesIO(resp.content))
            print(f"Valid image of size {img.size}")
        else:
            print(f"Returned content starts with: {resp.content[:100]}")
    except Exception as e:
        print(f"Error: {e}")
