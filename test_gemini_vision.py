import google.generativeai as genai
import sys

def test_gemini_image(api_key):
    genai.configure(api_key=api_key)
    
    # Try using a known image generation model
    # User's list has models/gemini-3-pro-image-preview, models/gemini-3.1-flash-image-preview
    # Oh wait, the new API for images is different in SDK?
    
    try:
        print("Using genai.ImageGenerationModel...")
        # SDK 0.8+ has ImageGenerationModel
        model = genai.ImageGenerationModel("models/gemini-3.1-flash-image-preview")
        result = model.generate_images(
            prompt="A cute flat illustration of a cat programming",
            number_of_images=1,
            aspect_ratio="16:9"
        )
        for i, img in enumerate(result.images):
            print(f"Success! Image {i} generated. Size: {len(img.image.image_bytes)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_gemini_image(sys.argv[1])
    else:
        print("Please provide API key")
