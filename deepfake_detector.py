from transformers import pipeline
from PIL import Image

fake_image_detector = pipeline("image-classification", model="umm-maybe/AI-image-detector")

def detect_fake(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        results = fake_image_detector(image)
        
        top_result = results[0]
        label = top_result['label'].lower()
        confidence = int(top_result['score'] * 100)
        
        if "artificial" in label or "fake" in label or "ai" in label:
            return "⚠️ AI Generated (Deepfake)", confidence, "High probability of AI manipulation."
        else:
            return "✅ Likely Real", confidence, "Natural features detected."
    except Exception as e:
        return "❌ Error", 0, str(e)