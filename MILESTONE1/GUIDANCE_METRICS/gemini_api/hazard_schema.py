# hazard_schema.py  — Pydantic v2 compatible (v3.0 with haptics + traffic lights)
from __future__ import annotations
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationError, confloat, conlist

PROMPT_VERSION = "3.0"  # v3.0 adds haptics and traffic light detection

ALLOWED_TYPES = {
    "trafficcone","person","vehicle","bicycle","motorcycle","stroller","barrier",
    "fence","gatearm","construction","debris","pole","signpost","bollard","step",
    "curb","openhole","puddle","crack","uneven","ramp","trolley","door","furniture",
    "planter","vegetation","dog","leash","cart","ladder","pallet","scaffold","wire",
    "rope","rail","bench","trashcan","mailbox","hydrant","scooter","wheelchair",
    "crate","box","bag","suitcase"
}

CANON = {
    "cone": "trafficcone", "car": "vehicle", "truck": "vehicle", "van": "vehicle",
    "bike": "bicycle", "sign": "signpost", "bollards": "bollard"
}

class TrafficLightInfo(BaseModel):
    approximate_distance_meters: int = Field(ge=0)
    description: str = Field(max_length=200)
    requires_deep_analyze: bool = True

class HazardOutput(BaseModel):
    hazard_detected: bool
    num_hazards: int = Field(ge=0)
    # v2: use min_length instead of min_items
    hazard_types: conlist(str, min_length=0)
    one_sentence: str = Field(min_length=1, max_length=200)  # v2.0: increased from 140
    evasive_suggestion: str = Field(min_length=1, max_length=250)  # v2.0: increased from 160
    bearing: str
    proximity: str
    confidence: confloat(ge=0.0, le=1.0)
    notes: str = Field(max_length=300)  # v2.0: explicit limit for notes (~40 words)

    # v3.0: NEW FIELDS
    haptic_recommendation: str = "no_haptic"  # left_haptic | right_haptic | full_haptic | no_haptic
    traffic_light_detected: bool = False
    traffic_light_info: Optional[TrafficLightInfo] = None

    def normalized(self) -> "HazardOutput":
        d = self.model_dump()

        # guardrails
        if not d["hazard_detected"]:
            d["num_hazards"] = 0
            d["hazard_types"] = []
        if d["hazard_detected"] and d["num_hazards"] == 0:
            d["num_hazards"] = 1
        if d["hazard_detected"] and not d["hazard_types"]:
            d["hazard_types"] = ["debris"]

        # canonicalize + lowercase
        d["bearing"] = str(d["bearing"]).lower().strip()
        d["proximity"] = str(d["proximity"]).lower().strip()

        norm_types: List[str] = []
        for t in d["hazard_types"]:
            t = CANON.get(t.lower(), t.lower())
            norm_types.append(t)

        # dedupe + filter to allowed set
        d["hazard_types"] = [t for t in dict.fromkeys(norm_types) if t in ALLOWED_TYPES]

        # clamp confidence defensively
        c = float(d["confidence"])
        d["confidence"] = max(0.0, min(1.0, c))

        # v3.0: Normalize haptic recommendation
        haptic = d.get("haptic_recommendation", "no_haptic").lower().strip()
        if haptic not in ["left_haptic", "right_haptic", "full_haptic", "no_haptic"]:
            # Auto-generate based on bearing + proximity if invalid
            if d["proximity"] == "near" and d["hazard_detected"]:
                if d["bearing"] == "left":
                    haptic = "left_haptic"
                elif d["bearing"] == "right":
                    haptic = "right_haptic"
                elif d["bearing"] == "center":
                    haptic = "full_haptic"
                else:
                    haptic = "no_haptic"
            else:
                haptic = "no_haptic"
        d["haptic_recommendation"] = haptic

        # v3.0: Normalize traffic light detection
        if not d.get("traffic_light_detected"):
            d["traffic_light_detected"] = False
            d["traffic_light_info"] = None

        return HazardOutput(**d)

class OutputEnvelope(BaseModel):
    _meta: dict
    result: HazardOutput
