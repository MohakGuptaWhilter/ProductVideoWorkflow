import httpx
import json
import os
from dotenv import load_dotenv, set_key
load_dotenv()
import base64
import asyncio
import time
# from kling_api import encode_jwt_token
KLING_API_URL = "https://api.klingai.com/v1/videos/omni-video"
KLING_API_KEY = os.getenv("KLING_API_KEY")

# def get_kling_auth_header():
#     AK = os.getenv("KLING_ACCESS_KEY")
#     SK = os.getenv("KLING_SECRET_KEY")
#     token = encode_jwt_token(AK, SK)
#     set_key(".env","KLING_API_KEY", token)

#     return f"Bearer {token}"


async def generate_kling_video_async(
    prompt: str,
    first_image_url: str,
    last_image_url: str,
):
    
    """
    Generates a video using Kling multi-image image2video API.
    """
    try:
        print("Inside step 8: kling video for ad")

        payload = {
        "model_name": "kling-video-o1",      # better model than kling-v1 [web:64][web:82]
        "prompt": prompt,
        "image_list": [
                {
                    "image_url": first_image_url,
                    "type": "first_frame",
                },
                {
                    "image_url": last_image_url,
                    "type": "end_frame",
                },
            ],
            "mode": "pro",                       # high-quality mode [web:64]
        }

        async def _post(headers):
            async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
                return await client.post(
                    KLING_API_URL,
                    headers=headers,
                    json=payload,
                )

        # ---- First attempt ----
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KLING_API_KEY}",
        }

        response = await _post(headers)


        # ---- Final error handling ----
        if response.status_code >= 400:
            raise RuntimeError(
                f"[Video] Kling API failed "
                f"({response.status_code}): {response.text}"
            )

        print(f"✅ Kling video task created successfully")
        return response.json()
    except Exception as e:
        print(str(e))
        raise


async def query_multi_image2video_task(
    task_id: str | None = None,
    external_task_id: str | None = None,
):
    """
    Query Multi-Image-to-Video task status.
    You must provide either task_id or external_task_id.
    """

    if not task_id and not external_task_id:
        raise ValueError("Either task_id or external_task_id must be provided")

    # Choose which ID to use in path
    task_identifier = task_id or external_task_id

    url = f"{KLING_API_URL}/{task_identifier}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KLING_API_KEY}",
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    except httpx.ReadTimeout:
        print("⚠️ Kling GET timed out — retrying...")
        return None

    except httpx.ConnectError as e:
        print(f"⚠️ Kling connection error — retrying... ({e})")
        return None

    except httpx.HTTPStatusError as e:
        # This is a REAL API error (4xx / 5xx)
        raise RuntimeError(f"Kling GET failed: {e.response.text}")


async def poll_kling_task_until_done(task_id: str, poll_interval: int = 3, timeout: int = 1800):
    """
    Repeatedly calls GET /image2video/{task_id}
    until task_status == 'succeed' or 'failed'
    """

    start_time = time.time()

    while True:
        result = await query_multi_image2video_task(task_id=task_id)

        if not result:
            print("⚠️ Empty response from Kling — retrying...")
            await asyncio.sleep(2)
            continue

        if "data" not in result:
            print("⚠️ Invalid response:", result)
            await asyncio.sleep(2)
            continue

        task_status = result["data"].get("task_status", "").lower()

        if task_status == "succeed":
            print("✅ Kling task succeeded")
            return result

        if task_status == "failed":
            raise RuntimeError(f"❌ Kling task failed: {result}")

        if time.time() - start_time > timeout:
            raise TimeoutError("⏰ Kling task polling timed out")

        # print(f"⏳ Task status: {task_status} — waiting...")
        await asyncio.sleep(poll_interval)


async def main():
    with open('video_prompts_final.json','r') as f:
        arr = json.load(f)
    first = arr["RootModel"][0]

    res = await generate_kling_video_async(first["prompt"], first["Initial_frame"],first["last_frame"])
    task_id = res["data"]["task_id"]
    final = await poll_kling_task_until_done(task_id)
    print(final)

# asyncio.run(main())
