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

load_dotenv()
SEM = asyncio.Semaphore(5)


async def handle_single_kling_task(task_id: str):
    async with SEM:
        final = await poll_kling_task_until_done(task_id)
        print("Final")
        print(final)
    return final["data"]["task_result"]["videos"][0]["url"]

#Submit a kling video task
async def submit_kling_tasks(video_prompts):
    submissions = []

    for d in video_prompts["RootModel"]:
        res = await generate_kling_video_async(
            d["prompt"],
            d["Initial_frame"],
            d["last_frame"]
        )
        submissions.append({
            "task_id": res["data"]["task_id"],
            "meta": d
        })
    print("Submissions")
    print(submissions)
    return submissions

#Post process video
async def post_process_video(video_url: str):
    # Upload to S3 (async)
    s3url = await upload_kling_video_to_s3(video_url, "company-garden")

    payload = {
        "microbriefId": "1",
        "input_s3_url": s3url,
        "category": "SISO"
    }

    # Offload sync CPU work
    loop = asyncio.get_running_loop()
    assets = await loop.run_in_executor(None, process_video, payload)

    return assets

async def process_all_videos(video_prompts):
    submissions = await submit_kling_tasks(video_prompts)

    # Create poll tasks
    poll_tasks = {
        asyncio.create_task(handle_single_kling_task(s["task_id"])): s["task_id"]
        for s in submissions
    }

    results = []

    for finished_task in asyncio.as_completed(poll_tasks):
        try:
            video_url = await finished_task

            # Immediately post-process when ready
            assets = await post_process_video(video_url)
            results.append(assets)

        except Exception as e:
            print(f"❌ Task failed: {e}")

    return results


async def video_gen_parallel(first_agent:dict):
    prompt_for_fourth = build_image_prompt_array(first_agent)

    with open('prompt_for_fourth.json','w') as f:
        json.dump(prompt_for_fourth,f,indent=4)
    
    fourth_agent = await run_visual_director(prompt_for_fourth)

    fifth_agent = await run_video_generation(fourth_agent)
    return fifth_agent

async def run_workflow(image_path, microbrief):
    
    first_agent = await run_meta_performance_visual_strategist(json.dumps(microbrief))
    
    second_agent = await run_nano_banana_prompter(first_agent)
    
    fifth_agent,images = await asyncio.gather(video_gen_parallel(first_agent), generate_nano_banana_images_async(second_agent,image_path,"company-garden","nano-banana/sunscreen"))


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

    #asynchronous video generation(fast)
    # results = await process_all_videos(video_prompts)

    # with open('after-post-process','w') as f:
    #     json.dump(results,f,indent=4)
    # Test 1
    print(final_assets)
    return final_assets

if __name__=="__main__":
    microbrief ={
        "product_info": {
            "name": "Mamaearth Sunscreen",
            "brand_guide": "Creative Diversity is the focus. Make skincare feel calm, clean, and trustworthy: soft daylight realism, minimal routines, texture-first macros, transparent 'how to apply' demos, doodle overlays that educate simply. Avoid loud claims—earn trust through clarity, gentle proof, and everyday relatability.",
            "content_strategy": {
            "persona": "The Routine Beginner (18–30) is trying to get skincare right without feeling judged. They want a sunscreen that doesn’t feel heavy, doesn’t leave visible residue, and fits under makeup or daily life. Barriers: sensory dislike (greasy feel), confusion about reapplication, fear of white cast in photos, and skepticism from past bad experiences. Trigger: a sunscreen that feels invisible, layers well, and is easy to make a daily habit.",
            "RTB_Feature": "Lightweight daily sun protection that feels comfortable on skin—easy to apply, easy to reapply, and designed to sit well in real routines.",
            "core_theme": "When sunscreen feels annoying (sticky, heavy, visible), you skip it—and the habit never forms.",
            "possible_hooks": [
                "Sunscreen you won’t want to skip.",
                "Feels like nothing. Does its job.",
                "The easiest routine win."
            ]
            }
        },
        "visual style": "clean skincare minimalism (soft daylight, airy backgrounds, texture macros, gentle educational overlays)"
        }
    asyncio.run(run_workflow("product.png",microbrief))