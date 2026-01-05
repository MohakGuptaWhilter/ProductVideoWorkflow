import os
import asyncio
from typing import Dict, Any
from PIL import Image, ImageFile
from google import genai
import json
from dotenv import load_dotenv
from google.genai import types
from functools import partial
import boto3
from urllib.parse import quote_plus    
from google import genai
from google.genai import types


MAX_CONCURRENT_GENERATIONS = 4 
load_dotenv()



s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
)

def upload_to_s3(local_path: str, bucket: str, key: str) -> str:
    s3.upload_file(
        Filename=local_path,
        Bucket=bucket,
        Key=key,
        ExtraArgs={"ContentType": "image/png"},
    )

    return f"https://{bucket}.s3.amazonaws.com/{quote_plus(key)}"

def _generate_single_image(
    shot_id: int,
    prompt: str,
    product_image_path: str,
    bucket: str,
    s3_prefix: str,
    aspect_ratio: str = "9:16",
    resolution: str = "2k",
) -> str:


    ImageFile.LOAD_TRUNCATED_IMAGES = True

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    os.makedirs("tmp", exist_ok=True)
    local_path = f"tmp/shot_{shot_id}.png"

    # 🔒 Load product image fresh per thread
    with Image.open(product_image_path) as product_image:
        product_image.load()

        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt, product_image],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=resolution,
                ),
            ),
        )

    for part in response.parts:
        image = part.as_image()
        if image is not None:
            image.save(local_path)

    # ☁️ Upload to S3
    s3_key = f"{s3_prefix}/shot_{shot_id}.png"
    s3_url = upload_to_s3(local_path, bucket, s3_key)

    # 🧹 Cleanup
    # os.remove(local_path)

    return s3_url


async def generate_nano_banana_images_async(
    prompt_payload: Dict[str, Any],
    product_image_path: str,
    bucket: str,
    s3_prefix: str,
    aspect_ratio: str = "9:16",
    resolution: str = "1k",
) -> Dict[int, str | None]:

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_GENERATIONS)
    prompts: List[Dict[str, Any]] = prompt_payload["prompts"]

    async def run_one(item):
        async with semaphore:
            return await asyncio.to_thread(
                _generate_single_image,
                item["shot_id"],
                item["prompt"],
                product_image_path,
                bucket,
                s3_prefix,
                aspect_ratio,
                resolution,
            )

    tasks = [run_one(item) for item in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output: Dict[int, str | None] = {}

    for item, result in zip(prompts, results):
        shot_id = item["shot_id"]
        if isinstance(result, Exception):
            print(f"❌ Shot {shot_id} failed: {result}")
            output[shot_id] = None
        else:
            output[shot_id] = result

    return output


if __name__=="__main__":
    with open('second_agent.json','r') as f:
        res = json.load(f)
    
    output_shots = asyncio.run(generate_nano_banana_images_async(res,"product.png","company-garden","nano-banana/sunscreen"))

    with open('third_agent.json','w') as f:
        json.dump(output_shots,f,indent=4)