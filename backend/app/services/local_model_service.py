import os
import json
import io
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # points to app/

with open(os.path.join(BASE_DIR, "class_mapping.json")) as f:
    mapping = json.load(f)

CLASSES = mapping["classes"]
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
model.load_state_dict(torch.load(os.path.join(BASE_DIR, "best_model.pth"), map_location=DEVICE))
model = model.to(DEVICE)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

EXPLANATIONS = {
    "Normal": "The trained CNN model analyzed the axial curvature map and did not detect patterns typically associated with corneal ectatic disorders.",
    "Suspect": "The trained CNN model detected some irregularities in the axial curvature pattern that warrant closer monitoring, though they are not definitively keratoconus.",
    "Keratoconus": "The trained CNN model detected curvature patterns consistent with keratoconus, such as localized steepening and asymmetry in the axial map.",
}


def analyze_topography_image_local(image_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(tensor)
        probabilities = torch.softmax(outputs, dim=1)[0]
        confidence, predicted_idx = torch.max(probabilities, dim=0)

    condition = CLASSES[predicted_idx.item()]

    return {
        "condition": condition,
        "confidence_percentage": round(confidence.item() * 100),
        "explanation": EXPLANATIONS.get(condition, "Analysis completed using the locally trained model."),
        "disclaimer": "This is an AI-generated preliminary observation, not a medical diagnosis. Please consult an ophthalmologist for proper evaluation.",
    }