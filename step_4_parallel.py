import os
from typing import Dict, Any, List
import json


def build_image_prompt_array(data: Dict) -> List[Dict[str, str]]:
    """
    Converts the 'shots' array from the input dictionary into
    an array of image prompt dictionaries in the required format.

    Output format:
    [
        {"image_0": "shot_id:1\nmagnification:Wide\nvisual_description:..."},
        {"image_1": "..."},
        ...
    ]
    """

    shots = data.get("shots", [])
    output: List[Dict[str, str]] = []

    for idx, shot in enumerate(shots):
        shot_id = shot.get("shot_id")
        magnification = shot.get("magnification")
        visual_description = shot.get("visual_description")

        formatted_prompt = (
            f"shot_id:{shot_id}\n"
            f"magnification:{magnification}\n"
            f"visual_description:{visual_description}"
        )

        output.append({
            f"image_{idx}": formatted_prompt
        })

    return output

if __name__=="__main__":
    with open('first_agent.json',"r") as f:
        res = json.load(f)
    output = build_image_prompt_array(res)

    with open('prompt_for_fourth.json','w') as f:
        json.dump(output,f,indent=4)