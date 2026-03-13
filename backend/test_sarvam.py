import os
import asyncio
import httpx

# I will use the key exactly from docker-compose.yml
SARVAM_API_KEY = "sk_qa7h42pu_P9J2uIuUafUFxnfuY5TAdY3K"

async def test_sarvam():
    url = "https://api.sarvam.ai/translate"
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "input": "नमस्ते डॉक्टर, मुझे दो दिन से बुखार है",
        "source_language_code": "hi-IN",
        "target_language_code": "en-IN"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        print("Status Code:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    asyncio.run(test_sarvam())
