import os
import asyncio
from typing import Dict, Any
from models import VideoEditingOutput
import json
from dotenv import load_dotenv
import yaml
from agents import Agent, Runner, function_tool


load_dotenv()

with open("config.yaml","r") as f:
    config = yaml.safe_load(f)

visual_director = config["video_director_and_editor"]

thinker = Agent(
    name="thinker",
    instructions="You are an AI reasoning agent. Analyze every request in depth, think step-by-step, and provide detailed, structured output. Do not skip reasoning. Do not guess blindly. Respond clearly, logically, and with full explanation.",
    model="gpt-5-mini"
)

tool = thinker.as_tool(
        tool_name="thinker",
        tool_description=(
    "Use this tool to perform deep step-by-step reasoning, analysis, "
    "and validation before producing the final output. "
    "Call this when the task requires logical breakdown, "
    "decision justification, constraint checking, or complex planning. "
    "The tool returns a fully reasoned analysis to guide the final response."
        ))

visual_director_agent = Agent(
    name = visual_director["name"],
    instructions = visual_director["instructions"],
    model= visual_director["model"],
    tools= [tool],
    output_type= VideoEditingOutput
)



async def run_visual_director(input_img:dict):
    try:
        print("Inside fourth agent: run visual director for ad")
        inputStr = json.dumps(input_img)

        output = await Runner.run(visual_director_agent,inputStr)

        result =output.final_output.model_dump()

        with open('fourth_agent.json','w') as f:
            json.dump(result,f,indent=4)
        
        return result
    except Exception as e:
        print(str(e))
        raise


if __name__ == "__main__":
    with open('prompt_for_fourth.json','r') as f:
        res = json.load(f)
    asyncio.run(run_visual_director(res))