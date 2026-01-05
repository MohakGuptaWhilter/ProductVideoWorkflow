import os
import asyncio
from typing import Dict, Any
from models import VideoEditingOutput
import json
from dotenv import load_dotenv
import yaml
from agents import Agent, Runner, function_tool

def s3urls_fifth_agent(images:dict):
    return {
        "s3-urls": list(images.values())
    }

def merge(images:dict, video_gen:dict):
    output = []
    s3urls = s3urls_fifth_agent(images)
    output.append(s3urls)
    output.append(video_gen)
    return output

if __name__=="__main__":
    r1=None
    r2=None

    with open('third_agent.json','r') as f:
        r1 = json.load(f)

    with open('fifth_agent.json','r') as f:
        r2 = json.load(f)

    ans = merge(r1,r2)

    with open('merged.json','w') as f:
        json.dump(ans,f,indent=4)
    

    