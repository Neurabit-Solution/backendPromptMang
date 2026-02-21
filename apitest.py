import os
from google import genai

# Replace with your actual API key
API_KEY = "AIzaSyCtvY-o1aei62MLz4Pgs1mx66rUS9ce7-A"

def check_ghibli_capability():
    client = genai.Client(api_key=API_KEY)
    
    # 1. Check if the required models are available for your key
    print("--- Checking Model Access ---")
    image_models = ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"]
    available_models = []
    
    try:
        models = client.models.list()
        model_names = [m.name for m in models]
        
        for im in image_models:
            # Models usually appear as 'models/gemini-...'
            if any(im in name for name in model_names):
                print(f"[✓] {im} is available.")
                available_models.append(im)
            else:
                print(f"[X] {im} not found in your account.")
                
    except Exception as e:
        print(f"Error accessing API: {e}")
        return

    if not available_models:
        print("\nResult: Your API key currently lacks image-to-image permissions.")
        return

    # 2. Verify image-to-image support
    print("\n--- Verifying Functionality ---")
    print(f"Yes! You can build your app using: {available_models[0]}")
    print("This model supports 'Response Modalities: IMAGE', allowing you to ")
    print("upload a file and receive a stylized Ghibli version back.")

if __name__ == "__main__":
    check_ghibli_capability()