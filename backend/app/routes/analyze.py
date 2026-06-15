from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services.groq_service import analyze_topography_image
from app.services.local_model_service import analyze_topography_image_local

router = APIRouter()

@router.post("/analyze/cornea-topography")
async def analyze_cornea_topography(
    file: UploadFile = File(...),
    model: str = Form("groq"),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()

    if model == "local":
        result = analyze_topography_image_local(image_bytes)
    else:
        result = analyze_topography_image(image_bytes, mime_type=file.content_type)

    result["model_used"] = model
    return result