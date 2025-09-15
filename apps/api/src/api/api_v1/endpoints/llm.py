from fastapi import APIRouter, HTTPException
from openai import AsyncOpenAI
from src.schemas.llm import LLMRequest, LLMResponse
from src.config import settings

router = APIRouter()
client = AsyncOpenAI(api_key=getattr(settings, "OPENAI_API_KEY", None))

@router.post("/structure", response_model=LLMResponse, tags=["llm"], summary="Generate a structured plan")
async def structure(body: LLMRequest) -> LLMResponse:
    if client.api_key is None:
        raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY")

    instructions = "Return ONLY JSON that matches the StructuredPlan model."

    msgs = getattr(body, "messages", None) or []
    sys = " ".join(m["content"] for m in msgs if m.get("role") in ("system", "developer"))
    usr = " ".join(m["content"] for m in msgs if m.get("role") == "user")

    try:
        resp = await client.responses.parse(
            model=(getattr(body, "model", None) or "gpt-5-mini"),
            instructions=instructions,
            input=body.input,
            text_format=LLMResponse,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail={"error": str(e)})

    if resp.output_parsed is None:
        raise HTTPException(status_code=502, detail="No parsed output from model")

    return resp.output_parsed