import os
import asyncio
from typing import Dict, Any
from models import VideoEditingOutput
import json
from dotenv import load_dotenv
import yaml
from agents import Agent, Runner
from models import VideoGenerationOutput


load_dotenv()

with open("config.yaml","r") as f:
    config = yaml.safe_load(f)

video_gen = config["video_generation"]

video_gen_agent = Agent(
    name = video_gen["name"],
    instructions = video_gen["instructions"],
    model= video_gen["model"],
    output_type= VideoGenerationOutput
)

async def run_video_generation(input_prompt:dict):
    inputStr = json.dumps(input_prompt)

    output = await Runner.run(video_gen_agent,inputStr)

    result =output.final_output.model_dump()

    with open('fifth_agent.json','w') as f:
        json.dump(result,f,indent=4)
    
    return result


if __name__ == "__main__":
    with open('fourth_agent.json','r') as f:
        res = json.load(f)
    asyncio.run(run_video_generation(res))

