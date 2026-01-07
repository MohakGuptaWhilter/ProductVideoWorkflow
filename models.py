from pydantic import BaseModel,HttpUrl, Field, RootModel
from typing import List, Optional, Dict, Any

class MasterSetup(BaseModel):
    environment: str
    lighting: str
    palette: str

class Shot(BaseModel):
    shot_id: int = Field(ge=1, le=8)
    magnification: str  # Wide | Mid | Macro
    headline: str
    visual_description: str

class VisualVibeOutput(BaseModel):
    strategy_summary: str
    master_setup: MasterSetup
    shots: List[Shot]

class ShotPrompt(BaseModel):
    shot_id: int = Field(..., ge=1, description="Sequential shot number")
    prompt: str = Field(..., min_length=1, description="Full generated prompt for this shot")

class PromptOutput(BaseModel):
    prompts: List[ShotPrompt] = Field(
        ...,
        min_items=1,
        description="List of prompts, one per shot"
    )


class VideoClip(BaseModel):
    clip_id: int = Field(
        ...,
        description="Sequential clip index."
    )

    start_image_id: str = Field(
        ...,
        description="ID of the starting frame image (e.g., Img_X)."
    )

    end_image_id: str = Field(
        ...,
        description="ID of the ending frame image."
    )

    motion_type: str = Field(
        ...,
        description="Camera movement used (may contain combined motions)."
    )

    motion_prompt: str = Field(
        ...,
        description="Instruction for the AI video generator describing the camera movement."
    )

    rationale: str = Field(
        ...,
        description="Explanation for why the start and end frames are paired."
    )


class VideoEditingOutput(BaseModel):
    editing_strategy: str = Field(
        ...,
        description="High-level explanation of the chosen editing sequence."
    )

    camera_personality: str = Field(
        ...,
        description="Overall movement vibe or camera behavior."
    )

    video_sequence: List[VideoClip] = Field(
        ...,
        description="Ordered list of video clips."
    )

class VideoGenerationTask(BaseModel):
    clip_id: int = Field(
        ...,
        description="Sequential clip identifier."
    )

    start_image_id: str = Field(
        ...,
        description="ID of the starting frame image (e.g., Img_A)."
    )

    end_image_id: str = Field(
        ...,
        description="ID of the ending frame image (e.g., Img_B)."
    )

    final_prompt: str = Field(
        ...,
        description="Composed prompt combining movement, physics, and technical enhancers."
    )


class VideoGenerationOutput(BaseModel):
    video_generation_tasks: List[VideoGenerationTask] = Field(
        ...,
        description="List of video generation tasks."
    )

class FrameTransition(BaseModel):
    Initial_frame:str = Field(
        ...,
        description="S3 URL of the initial frame image"
    )
    last_frame:str = Field(
        ...,
        description="S3 URL of the last frame image"
    )
    prompt:str = Field(
        ...,
        description="Camera movement or cinematic transition prompt"
    )


class FrameTransitionList(BaseModel):
    RootModel: List[FrameTransition]

class BrandPrism(BaseModel):
    Physique: str
    Relationship: str
    Reflection: str
    Self-Image: str
    Culture: str
    Personality: str


class Color(BaseModel):
    hex: str
    type: str
    name: str


class BrandInfo(BaseModel):
    brand_prism: BrandPrism
    fonts: List[str]
    colors: List[Color]
    logos: List[str]


class ProductInfo(BaseModel):
    product_name: str
    product_description: str
    features: str
    product_images: List[str]


class MicroBriefInner(BaseModel):
    id: int
    persona: str
    reasonToBuy: str
    awarenessLevel: str
    brief: str
    mediaType: str
    mediaStyle: Optional[str]
    mediaOrientation: str


class MicroBrief(BaseModel):
    campaign_id: int
    brand_info: BrandInfo
    product_info: ProductInfo
    micro_brief: MicroBriefInner
