import asyncio
import httpx

async def test_sarvam_auto():
    url = "https://api.sarvam.ai/translate"
    headers = {
        "api-subscription-key": "sk_qa7h42pu_P9J2uIuUafUFxnfuY5TAdY3K",
        "Content-Type": "application/json"
    }
    # Testing with 'auto' as it was in original code
    payload = {
        "input": "नमस्ते डॉक्टर, मुझे दो दिन से बुखार है",
        "source_language_code": "Unknown", # Or auto
        "target_language_code": "en-IN"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            print("Status Code:", response.status_code)
            print("Response:", response.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test_sarvam_auto())
