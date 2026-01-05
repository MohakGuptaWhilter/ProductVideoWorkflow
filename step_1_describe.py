import yaml
from agents import Agent, Runner
from dotenv import load_dotenv
from models import VisualVibeOutput
import asyncio
import os
import base64
import json

load_dotenv()

with open("config.yaml","r") as f:
    config = yaml.safe_load(f)

meta_performance = config["meta_performance_visual_strategist"]

meta_performance = Agent(
    name = meta_performance["name"],
    instructions = meta_performance["instructions"],
    model= meta_performance["model"],
    output_type= VisualVibeOutput
)

def image_to_data_url(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    if ext == "jpg":
        ext = "jpeg"

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:image/{ext};base64,{b64}"


async def run_meta_performance_visual_strategist(microbrief:str):
    # image_url = image_to_data_url(img_path)
    messages = f"Microbrief: {microbrief}"
    result = await Runner.run(
        meta_performance,
        input=messages
    )

    first_agent_output = result.final_output.model_dump()
    with open('first_agent.json','w') as f:
        json.dump(first_agent_output,f,indent=4)
    return first_agent_output

if __name__=="__main__":
    microbrief ={
        "product_info": {
            "name": "Mamaearth Sunscreen",
            "brand_guide": "Creative Diversity is the focus. Make skincare feel calm, clean, and trustworthy: soft daylight realism, minimal routines, texture-first macros, transparent 'how to apply' demos, doodle overlays that educate simply. Avoid loud claims—earn trust through clarity, gentle proof, and everyday relatability.",
            "content_strategy": {
            "persona": "The Routine Beginner (18-30) is trying to get skincare right without feeling judged. They want a sunscreen that doesn’t feel heavy, doesn’t leave visible residue, and fits under makeup or daily life. Barriers: sensory dislike (greasy feel), confusion about reapplication, fear of white cast in photos, and skepticism from past bad experiences. Trigger: a sunscreen that feels invisible, layers well, and is easy to make a daily habit.",
            "RTB_Feature": "Lightweight daily sun protection that feels comfortable on skin—easy to apply, easy to reapply, and designed to sit well in real routines.",
            "core_theme": "When sunscreen feels annoying (sticky, heavy, visible), you skip it—and the habit never forms.",
            "possible_hooks": [
                "Sunscreen you won't want to skip.",
                "Feels like nothing. Does its job.",
                "The easiest routine win."
            ]
            }
        },
        "visual style": "clean skincare minimalism (soft daylight, airy backgrounds, texture macros, gentle educational overlays)"
        }

    asyncio.run(run_meta_performance_visual_strategist(json.dumps(microbrief)))

