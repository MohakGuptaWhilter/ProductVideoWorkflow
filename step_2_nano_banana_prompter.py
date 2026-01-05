import yaml
from agents import Agent, Runner
from dotenv import load_dotenv
from models import PromptOutput
import asyncio
import os
import base64
import json

load_dotenv()

with open("config.yaml","r") as f:
    config = yaml.safe_load(f)

nano_banana_prompt = config["nano_banana_technical_prompter"]

nano_banana_prompter = Agent(
    name = nano_banana_prompt["name"],
    instructions = nano_banana_prompt["instructions"],
    model= nano_banana_prompt["model"],
    output_type= PromptOutput
)

async def run_nano_banana_prompter(jsonOutput: dict):
    jsonStr = json.dumps(jsonOutput)
    messages = jsonStr

    nano_banana_prompts = await Runner.run(
        nano_banana_prompter, input=jsonStr
    )

    result = nano_banana_prompts.final_output.model_dump()

    with open('second_agent.json','w') as f:
        json.dump(result,f, indent=4)
    return result

if __name__=="__main__":
    jsonDict = None
    with open('first_agent.json','r') as f:
        jsonDict = json.load(f)

    asyncio.run(run_nano_banana_prompter(jsonDict))