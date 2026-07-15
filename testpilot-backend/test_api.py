"""快速测试 AI API 是否可用"""
import httpx
import asyncio
from app.config import get_settings

async def test_api():
    s = get_settings()
    url = f"{s.deepseek_base_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {s.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": s.deepseek_model,
        "messages": [{"role": "user", "content": "回复 ok"}],
        "max_tokens": 10,
    }
    print(f"URL: {url}")
    print(f"Model: {s.deepseek_model}")
    print(f"Key (前10位): {s.deepseek_api_key[:10]}...")
    print(f"Has key: {s.has_api_key}")
    print()

    async with httpx.AsyncClient(timeout=30, trust_env=False) as client:
        try:
            resp = await client.post(url, headers=headers, json=payload)
            print(f"Status: {resp.status_code}")
            print(f"Headers: {dict(resp.headers)}")
            print(f"Body (前500字): {resp.text[:500]}")
        except Exception as e:
            print(f"请求异常: {type(e).__name__}: {e}")

asyncio.run(test_api())
