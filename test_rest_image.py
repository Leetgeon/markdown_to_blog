import requests
import sys

def test(api_key):
    # Gemini Image Generation (Imagen) REST API Endpoint
    # Let's try gemini-2.5-flash-image assuming it supports generateContent
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "A cute flat illustration of a cat programming"}
                ]
            }
        ]
    }
    resp = requests.post(url, json=payload)
    print(resp.status_code)
    print(resp.text[:500])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test(sys.argv[1])
