from pydantic import BaseModel
from typing import List 

class ProtagonistProfile(BaseModel):
    core_trait: str
    primary_goal: str

class Episode(BaseModel):
    episode_number: int
    title: str
    click_title: str
    summary: str
    visual_storyboard: str
    emotion_tag: str
    open_loop: str
    viral_hook: str
    cliffhanger_action: str

class SeriesArc(BaseModel):
    series_title: str
    protagonist_profile: ProtagonistProfile
    episodes: List[Episode]