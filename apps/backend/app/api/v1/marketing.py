from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl
from typing import List
import httpx, asyncio

from app.services.marketing_qa.utm_validator import validate_utm
from app.services.marketing_qa.pixel_checker import check_pixels
from app.services.marketing_qa.copy_bias_scan import scan_copy
from app.services.marketing_qa.trust_score import compute_score

router = APIRouter(prefix="/v1/marketing", tags=["marketing"])

class MarketingQARequest(BaseModel):
    urls: List[HttpUrl]

class CheckResult(BaseModel):
    check: str
    status: str
    details: dict

class MarketingQAResponse(BaseModel):
    trust_score: int
    results: List[CheckResult]

@router.post("/qa/run", response_model=MarketingQAResponse)
async def run_marketing_qa(req: MarketingQARequest):
    results: list[dict] = []

    # UTM checks
    for u in req.urls:
        results.append(validate_utm(str(u)))

    # Pixel & simple copy scan (fetch once per URL)
    async with httpx.AsyncClient(timeout=10) as client:
        htmls = await asyncio.gather(*[client.get(str(u), follow_redirects=True) for u in req.urls])
    for r in htmls:
        url = str(r.request.url)

        # pixels
        pix = await check_pixels(url)
        results.append(pix)

        # copy (very naive on full HTML; refine to visible text later)
        results.append(scan_copy(r.text))

    score = compute_score(results)
    return {"trust_score": score, "results": results}
