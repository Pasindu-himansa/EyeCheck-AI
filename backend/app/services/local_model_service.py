import os
import json
import io
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "best_model.pth")
MAPPING_PATH = os.path.join(BASE_DIR, "class_mapping.json")

CLASSES = ["Normal", "Suspect", "Keratoconus"]

model = None
transform = None

if os.path.exists(MODEL_PATH) and os.path.exists(MAPPING_PATH):
    try:
        import torch
        import torch.nn as nn
        from torchvision import transforms, models

        DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        with open(MAPPING_PATH) as f:
            mapping = json.load(f)
        CLASSES = mapping["classes"]

        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model = model.to(DEVICE)
        model.eval()

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        print("Local model loaded successfully.")
    except Exception as e:
        print(f"Warning: Could not load local model: {e}")
        model = None
else:
    print("Local model files not found — local inference disabled.")

EXPLANATIONS = {
    "Normal": "The trained CNN model analyzed the axial curvature map and did not detect patterns typically associated with corneal ectatic disorders.",
    "Suspect": "The trained CNN model detected some irregularities in the axial curvature pattern that warrant closer monitoring, though they are not definitively keratoconus.",
    "Keratoconus": "The trained CNN model detected curvature patterns consistent with keratoconus, such as localized steepening and asymmetry in the axial map.",
}


def is_local_model_available() -> bool:
    return model is not None


def analyze_topography_image_local(image_bytes: bytes) -> dict:
    if model is None:
        return {
            "condition": "Unavailable",
            "confidence_percentage": 0,
            "explanation": "Local model is not available in this deployment. Please use the Groq AI model instead.",
            "disclaimer": "This is an AI-generated preliminary observation, not a medical diagnosis. Please consult an ophthalmologist for proper evaluation.",
        }

    import torch
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(tensor)
        probabilities = torch.softmax(outputs, dim=1)[0]
        confidence, predicted_idx = torch.max(probabilities, dim=0)

    condition = CLASSES[predicted_idx.item()]

    return {
        "condition": condition,
        "confidence_percentage": round(confidence.item() * 100),
        "explanation": EXPLANATIONS.get(condition, "Analysis completed."),
        "disclaimer": "This is an AI-generated preliminary observation, not a medical diagnosis. Please consult an ophthalmologist for proper evaluation.",
    }