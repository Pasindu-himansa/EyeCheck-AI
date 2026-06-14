from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.groq_service import analyze_topography_image

router = APIRouter()

@router.post("/analyze/cornea-topography")
async def analyze_cornea_topography(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()

    result = analyze_topography_image(image_bytes, mime_type=file.content_type)

    return result