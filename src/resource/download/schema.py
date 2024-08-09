from typing import Optional
from pydantic import BaseModel, Field


class VideoInfo(BaseModel):
    title: str
    thumbUrl: str
    url: str
    site: str


class VideoUrl(BaseModel):
    url: str


class ProgressInfo(BaseModel):
    download_id: int
    status: str
    percentage: float
    filename: str


class FormatInfo(BaseModel):
    format_id: str
    ext: str
    resolution: str
    fps: Optional[str] = Field(default=None)
    filesize: Optional[int] = Field(default=None)
    tbr: Optional[float]
    vcodec: str = Field(default="unknown")
    acodec: str = Field(default="unknown")
    format_note: str = Field(default="unknown")

    @classmethod
    def parse_obj(cls, obj):
        if "fps" in obj and obj["fps"] is not None:
            obj["fps"] = str(obj["fps"])
        if "filesize" not in obj:
            obj["filesize"] = None
        if "format_note" not in obj:
            obj["format_note"] = "unknown"
        return super().model_validate(obj)


class VideoProgress(BaseModel):
    url: str
    status: str
    percentage: float
    filename: str
