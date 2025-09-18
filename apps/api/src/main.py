from __future__ import annotations

from contextlib import asynccontextmanager
import json
from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from openai import AsyncOpenAI
from pydantic import BaseModel

from src.api.api_v1.api import api_router
from src.config import settings

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # add your dev domains as needed
]

class OpenAILLM:
    def __init__(self, client: AsyncOpenAI, model: str):
        self.client = client
        self.model = model

    @staticmethod
    def _to_wire_json(parsed: Any, chunks: List[str]) -> Dict[str, Any] | list:
        """Return a JSON-serializable object (dict/list) with aliases if it's Pydantic."""
        if parsed is not None:
        # Pydantic model -> dict (use aliases like nodeId/edgeId)
            if isinstance(parsed, BaseModel):
                return parsed.model_dump(by_alias=True)
            # Already JSON-y
            if isinstance(parsed, (dict, list)):
                return parsed
            # Sometimes SDKs hand back a JSON string
            if isinstance(parsed, str):
                try:
                    return json.loads(parsed)
                except json.JSONDecodeError:
                    return {"text": parsed}

            # Last-ditch: try common Pydantic-style methods without importing BaseModel
            if hasattr(parsed, "model_dump"):
                return parsed.model_dump(by_alias=True)  # type: ignore[attr-defined]
            if hasattr(parsed, "model_dump_json"):
                return json.loads(parsed.model_dump_json(by_alias=True))  # type: ignore[attr-defined]

        # No parsed object (e.g., refusal or plain text) → try to parse streamed text
        text = "".join(chunks).strip()
        if text:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"text": text}

        # Truly nothing
        return {"text": ""}

    async def generate_json(self, system: str, user: str, text_format: Any) -> dict | list:
        async with self.client.responses.stream(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            text_format=text_format,  # <- your Pydantic model (e.g., Graph)
        ) as stream:
            chunks: List[str] = []
            async for event in stream:
                et = getattr(event, "type", "")
                if et in ("response.output_text.delta",
                        "response.text.delta",
                        "response.refusal.delta"):
                    delta = getattr(event, "delta", None)
                    if delta is not None:
                        chunks.append(delta)
                elif et == "response.error":
                    raise RuntimeError(getattr(event, "error", "Unknown stream error"))

            final = await stream.get_final_response()
            parsed = getattr(final, "output_parsed", None)
            return self._to_wire_json(parsed, chunks)

# Simple health/info router
info_router = APIRouter()

@info_router.get("/", status_code=200, include_in_schema=False)
async def info():
    return [{"Status": "API Running"}]

# Custom operationId (keeps your codegen stable)
def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"

# Lifespan wires app.state.llm_client once
@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = settings.OPENAI_API_KEY
    model = settings.OPENAI_MODEL
    client = AsyncOpenAI(api_key=api_key)
    app.state.llm_client = OpenAILLM(client, model)
    yield
    # teardown not required

def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        generate_unique_id_function=custom_generate_unique_id,
        root_path=settings.ROOT,
        root_path_in_servers=True,
        lifespan=lifespan,                     # <-- keep lifespan on the ONLY app instance
    )

    # Routers
    app.include_router(api_router, prefix=settings.API_VERSION)
    app.include_router(info_router, tags=[""])

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = get_application()