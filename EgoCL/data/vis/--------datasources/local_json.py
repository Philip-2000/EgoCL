import json
import os
from typing import List, Optional, Dict, Any


class LocalJsonDataSource:
    """Simple JSON-backed datasource for prototyping.

    JSON schema example:
    {
      "videos": [
        {
          "id": "sample",
          "title": "示例视频",
          "path": "sample.mp4",  # relative to base_dir or absolute
          "mime_type": "video/mp4",
          "annotations": [
            {"category": "事件", "start": 1, "end": 10, "label": "和李华一起吃饭"},
            {"category": "事件", "start": 10, "end": 50, "label": "吃完饭去洗碗"}
          ]
        }
      ]
    }
    """

    def __init__(self, json_path: str, base_dir: Optional[str] = None) -> None:
        self.json_path = json_path
        self.base_dir = base_dir or os.getcwd()
        self._data = {"videos": []}
        self._load()

    def _load(self):
        if not os.path.exists(self.json_path):
            # keep empty
            self._data = {"videos": []}
            return
        with open(self.json_path, "r", encoding="utf-8") as f:
            self._data = json.load(f) or {"videos": []}

    def _find(self, video_id: str) -> Optional[Dict[str, Any]]:
        for v in self._data.get("videos", []):
            if v.get("id") == video_id:
                return v
        return None

    def list_videos(self) -> List[Dict[str, Any]]:
        return [
            {"id": v.get("id"), "title": v.get("title") or v.get("id")}
            for v in self._data.get("videos", [])
        ]

    def get_video_path(self, video_id: str) -> Optional[str]:
        v = self._find(video_id)
        if not v:
            return None
        path = v.get("path")
        if not path:
            return None
        if not os.path.isabs(path):
            path = os.path.join(self.base_dir, path)
        return path

    def get_annotations(self, video_id: str) -> Optional[List[Dict[str, Any]]]:
        v = self._find(video_id)
        if not v:
            return None
        return v.get("annotations") or []

    def get_mime_type(self, video_id: str) -> Optional[str]:
        v = self._find(video_id)
        if not v:
            return None
        return v.get("mime_type")
