import google.generativeai as genai
import sys
import os

def test_image(api_key):
    genai.configure(api_key=api_key)
    try:
        models = genai.list_models()
        image_models = [m.name for m in models if 'image' in m.name.lower()]
        print("Available Image Models:", image_models)
        
        if not image_models:
            print("No image models found.")
            return

        target_model = image_models[0]
        print(f"Testing {target_model}...")
        
        # 최신 SDK에서는 genai.ImageGenerationModel 이 존재할 수 있습니다.
        if hasattr(genai, 'ImageGenerationModel'):
            print("Using ImageGenerationModel...")
            m = genai.ImageGenerationModel(target_model)
            result = m.generate_images(prompt="A cute cat", number_of_images=1)
            print("Success! Image generated.")
        else:
            print("No ImageGenerationModel in SDK.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_image(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GEMINI_API_KEY", ""))
