import os
import asyncio
from typing import Dict, Any
from models import VideoEditingOutput
import json
from dotenv import load_dotenv
import yaml
from agents import Agent, Runner
from models import FrameTransitionList


load_dotenv()

with open("config.yaml","r") as f:
    config = yaml.safe_load(f)

frame_transition = config["aggregator"]

frame_transition_agent = Agent(
    name = frame_transition["name"],
    instructions = frame_transition["instructions"],
    model = frame_transition["model"],
    output_type= FrameTransitionList
)

async def run_frame_transition(whole:dict):
    # with open('merged.json','r') as f:
    #     whole = json.load(f)
    
    messages =(
        f"Image_urls: {json.dumps(whole[0]["s3-urls"])}"
        f"Pairs: {json.dumps(whole[1]["video_generation_tasks"])}"
    )

    print(messages)
    output = await Runner.run(frame_transition_agent,messages)
    result = output.final_output.model_dump()

    with open('video_prompts_final.json','w') as f:
        json.dump(result,f, indent=4)

    return result

if __name__=="__main__":
    with open('merged.json','r') as f:
        whole = json.load(f)
    asyncio.run(run_frame_transition(whole))

