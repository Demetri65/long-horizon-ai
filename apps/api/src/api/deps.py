from typing import Annotated, AsyncGenerator, Optional

from fastapi import Depends, HTTPException
from supabase import AsyncClient, acreate_client, AsyncClientOptions

from src.config import settings


async def get_db() -> AsyncGenerator[AsyncClient, None]:
    client: Optional[AsyncClient] = None
    try:
        client = await acreate_client(
            settings.DB_URL,
            settings.DB_API_KEY,
            options=AsyncClientOptions(
                postgrest_client_timeout=10, storage_client_timeout=10
            ),
        )
        # client = await client.auth.sign_in_with_password(
        #     {"email": settings.DB_EMAIL, "password": settings.DB_PASSWORD}
        # )
        yield client

    except Exception as e:
        print(e)
        raise


SessionDep = Annotated[AsyncClient, Depends(get_db)]
