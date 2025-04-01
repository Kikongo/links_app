import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_short_link():
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        response = await ac.post("/link/links/shorten", json={"original_url": "https://example.com"})
    
    assert response.status_code == 200
    assert "short_url" in response.json()

@pytest.mark.asyncio
async def test_redirect_short_link():
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        create_response = await ac.post("/link/links/shorten", json={"original_url": "https://example.com"})
        short_code = create_response.json()["short_url"].split("/")[-1]

        response = await ac.get(f"link/{short_code}")
    
    assert response.status_code == 200
    assert response.json()["redirect"] == "https://example.com/"

@pytest.mark.asyncio
async def test_get_link_stats():
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        create_response = await ac.post("/link/links/shorten", json={"original_url": "https://example.com"})
        short_code = create_response.json()["short_url"].split("/")[-1]

        stats_response = await ac.get(f"link/links/{short_code}/stats")

    assert stats_response.status_code == 200
    assert "visit_count" in stats_response.json()
