from typing import List
from pydantic import BaseModel, Field


class PlotOutput(BaseModel):
    id: int = Field(description="id of the image")
    key_insight: List[str] = Field(
        description="list of key insights derived from graphs"
    )


class PlotList(BaseModel):
    images: List[PlotOutput] = Field(description="A list containing images data")
    overall_insight: str = Field(description="A high-level summary of all findings")
