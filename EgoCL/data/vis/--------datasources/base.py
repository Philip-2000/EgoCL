from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod


class BaseVideoDataSource(ABC):
    """Abstract datasource for videos and annotations.

    Annotation schema:
    {
        "id": str,
        "title": str,
        "path": str,  # absolute or relative to base_dir
        "mime_type": str | None,
        "annotations": [
            {"category": str, "start": float, "end": float, "label": str}
        ]
    }
    """

    @abstractmethod
    def list_videos(self) -> List[Dict[str, Any]]:
        """Return a list of video descriptors with keys: id, title."""
        ...

    @abstractmethod
    def get_video_path(self, video_id: str) -> Optional[str]:
        """Return absolute filesystem path for the video."""
        ...

    @abstractmethod
    def get_annotations(self, video_id: str) -> Optional[List[Dict[str, Any]]]:
        """Return list of annotations for the video_id."""
        ...

    def get_mime_type(self, video_id: str) -> Optional[str]:
        """Optionally return a mime type string like 'video/mp4'."""
        return None
