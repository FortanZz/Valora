from typing import List

from fastapi import APIRouter

from app.schemas.property import PropertyResponse

router = APIRouter(prefix="/api/v1/properties", tags=["properties"])


@router.get("/", response_model=List[PropertyResponse])
def list_properties() -> List[PropertyResponse]:
    return []
