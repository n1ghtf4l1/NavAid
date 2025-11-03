# navigation_guidance_schema.py — Combined navigation + hazard detection
from __future__ import annotations
from typing import Optional

from pydantic import BaseModel, Field, confloat

PROMPT_VERSION = "3.0"  # Combined guidance system

class TrafficLightInfo(BaseModel):
    approximate_distance_meters: int = Field(ge=0)
    description: str = Field(max_length=200)
    requires_deep_analyze: bool = True

class NavigationGuidanceOutput(BaseModel):
    """
    Combined output that merges Google Maps navigation with hazard detection.
    Gemini receives BOTH the navigation instruction and the photo.
    """
    # Hazard Detection
    hazard_detected: bool = False
    hazard_guidance: str = ""  # Spoken first if hazard exists
    haptic_recommendation: str = "no_haptic"  # left_haptic | right_haptic | full_haptic | no_haptic

    # Navigation Instruction
    navigation_instruction: str = Field(min_length=1, max_length=300)  # Enhanced Google Maps instruction

    # Traffic Light Detection
    traffic_light_detected: bool = False
    traffic_light_info: Optional[TrafficLightInfo] = None

    # Metadata
    confidence: confloat(ge=0.0, le=1.0) = 0.9
    notes: str = ""

    def normalized(self) -> "NavigationGuidanceOutput":
        d = self.model_dump()

        # Normalize haptic recommendation
        haptic = d.get("haptic_recommendation", "no_haptic").lower().strip()
        if haptic not in ["left_haptic", "right_haptic", "full_haptic", "no_haptic"]:
            haptic = "no_haptic"
        d["haptic_recommendation"] = haptic

        # Ensure hazard_guidance is empty if not detected
        if not d["hazard_detected"]:
            d["hazard_guidance"] = ""
            d["haptic_recommendation"] = "no_haptic"

        # Normalize traffic light detection
        if not d.get("traffic_light_detected"):
            d["traffic_light_detected"] = False
            d["traffic_light_info"] = None

        return NavigationGuidanceOutput(**d)

class OutputEnvelope(BaseModel):
    _meta: dict
    result: NavigationGuidanceOutput
