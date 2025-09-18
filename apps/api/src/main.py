from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from openai import AsyncOpenAI

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

    async def generate_json(self, system: str, user: str) -> dict:
      # Response format forces valid JSON in 'content'
      resp = await self.client.chat.completions.create(
          model=self.model,
          response_format={"type": "json_object"},
          messages=[
              {"role": "system", "content": system},
              {"role": "user", "content": user},
          ],
      )
      content = resp.choices[0].message.content or "{}"
      import json
      return json.loads(content)

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