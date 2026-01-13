import yaml
from agents import Agent, Runner
from dotenv import load_dotenv
from models import VisualVibeOutput
import asyncio
import os
import base64
import json
from step_1_describe import *
from step_2_nano_banana_prompter import *
from step_3_images import *
from step_4_parallel import *
from step_4_visual_director import *
from step_5_video_gen import *
from step_6_merge_images import *
from step_7_aggregator import *
from step_8_videos_kling import *
from step_9_upload_video_s3 import *
from speed_ramp.speedramp import *
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from models import CampaignRequest
import tempfile
import boto3
from urllib.parse import urlparse, unquote

load_dotenv()

app = FastAPI()


def download_from_s3(s3_url: str, local_path: str = "product.png") -> str:
    s3_url = unquote(s3_url).strip().strip('"')

    if s3_url.startswith("s3://"):
        parsed = urlparse(s3_url)
        bucket, key = parsed.netloc, parsed.path.lstrip("/")
    else:
        parsed = urlparse(s3_url)
        bucket = parsed.netloc.split(".")[0]
        key = parsed.path.lstrip("/")

    os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)

    boto3.client("s3").download_file(bucket, key, local_path)
    return local_path

async def video_gen_parallel(first_agent:dict):
    prompt_for_fourth = build_image_prompt_array(first_agent)

    with open('prompt_for_fourth.json','w') as f:
        json.dump(prompt_for_fourth,f,indent=4)
    
    fourth_agent = await run_visual_director(prompt_for_fourth)

    fifth_agent = await run_video_generation(fourth_agent)
    return fifth_agent

async def run_workflow(microbrief_dict: dict):
    try:
        image_s3_url = microbrief_dict["product_info"]["product_images"][0]
        campaign_id = microbrief_dict["campaign_id"]
        microbrief = microbrief_dict["micro_brief"]
        product_name = microbrief_dict["product_info"]["product_name"]

                # ✅ DOWNLOAD PRODUCT IMAGE ONCE
        # product_image = await asyncio.to_thread(
        #     download_from_s3, image_s3_url
        # )
        product_image = "product.png"

        first_agent = await run_meta_performance_visual_strategist(json.dumps(microbrief))
        
        second_agent = await run_nano_banana_prompter(first_agent)
        
        fifth_agent,images = await asyncio.gather(video_gen_parallel(first_agent), generate_nano_banana_images_async(second_agent,image_s3_url,"company-garden",f"nano-banana/{product_name}"))


        # merged = await asyncio.to_thread(merge, images, fifth_agent)
        merged = merge(images, fifth_agent)
            

        video_prompts = await run_frame_transition(merged)

        # first_dict = video_prompts["RootModel"][0]

        #synchronous video generation(slow)
        final_assets = []
        for first_dict in video_prompts["RootModel"]:
            res = await generate_kling_video_async(first_dict["prompt"],first_dict["Initial_frame"],first_dict["last_frame"])
            task_id = res["data"]["task_id"]
            print("🚀 Kling task submitted. You can safely exit now.")

            # print(res)
            # # sleep()

            final = await poll_kling_task_until_done(task_id)

            print(final)
            url = final["data"]["task_result"]["videos"][0]["url"]

            #Video Generation
            s3url= await upload_kling_video_to_s3(url,"company-garden")
            payload = {
                "microbriefId": "1",
                "input_s3_url": s3url,
                "category": "SISO"
            }
            assets = process_video(payload)
            final_assets.append(assets)
            print(assets)


        # Test 1
        print(final_assets)
        return final_assets
    except Exception as e:
        raise



@app.post("/generate-campaign-assets")
async def generate_campaign_assets(
    microbrief: CampaignRequest,
    background_tasks: BackgroundTasks
):
    microbrief_dict = microbrief.model_dump()

    # Basic validation
    product_images = microbrief_dict["product_info"].get("product_images", [])
    if not product_images:
        return {
            "status": "error",
            "message": "No product_images found in product_info"
        }

    # *Add pending status task*

    background_tasks.add_task(
        run_workflow,
        microbrief_dict
    )

    return {
        "status": "processing",
        "campaign_id": microbrief.campaign_id,
        "image_used": product_images[0]
    }

