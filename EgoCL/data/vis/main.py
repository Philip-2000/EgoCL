class APP():
    def __init__(self, ACTIVITIES):
        import os
        import sys
        import math
        import importlib
        from typing import Optional

        from fastapi import FastAPI, Request, HTTPException
        from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
        from fastapi.staticfiles import StaticFiles
        from fastapi.templating import Jinja2Templates
        from starlette.responses import Response
        from starlette.background import BackgroundTask

        # Ensure local package path is importable when running as a script
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)

        app = FastAPI(title="EgoCL Video Self-Check Service")

        # Mount static files
        app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

        # Templates
        templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

        # Data source (pluggable)
        # Can be swapped via env VIS_DATASOURCE_CLASS="module.path:ClassName"
        # DS_CLASS_PATH = os.environ.get("VIS_DATASOURCE_CLASS", "datasources.local_json:LocalJsonDataSource")
        # _mod_name, _cls_name = DS_CLASS_PATH.split(":") if ":" in DS_CLASS_PATH else (DS_CLASS_PATH, "LocalJsonDataSource")
        # _mod = importlib.import_module(_mod_name)
        # DS_CLS = getattr(_mod, _cls_name)
        # DATA_SOURCE = DS_CLS(
        #     json_path=os.environ.get(
        #         "VIS_ANNOTATIONS_JSON",
        #         os.path.join(BASE_DIR, "sample_data", "annotations.json"),
        #     ),
        #     base_dir=os.environ.get(
        #         "VIS_VIDEOS_BASE_DIR",
        #         os.path.join(BASE_DIR, "sample_data"),
        #     ),
        # )
        from .Vis_Activities import VisActivities
        DATA_SOURCE = VisActivities(ACTIVITIES)



        @app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            return templates.TemplateResponse("index.html", {"request": request})


        @app.get("/api/videos")
        async def list_videos():
            videos = DATA_SOURCE.list_videos()
            return {"videos": videos}


        @app.get("/api/videos/{video_id}/annotations")
        async def get_annotations(video_id: str):
            annotations = DATA_SOURCE.get_annotations(video_id)
            print(len(annotations))
            if annotations is None:
                raise HTTPException(status_code=404, detail="Video not found or annotations missing")
            return {"video_id": video_id, "annotations": annotations}


        def _file_iterator(file, start: int, end: int, chunk_size: int = 1024 * 1024):
            """Yield file chunks from start to end inclusive."""
            file.seek(start)
            bytes_left = end - start + 1
            while bytes_left > 0:
                read_size = min(chunk_size, bytes_left)
                data = file.read(read_size)
                if not data:
                    break
                bytes_left -= len(data)
                yield data


        @app.get("/video/{video_id}")
        async def stream_video(video_id: str, request: Request):
            print(f"Streaming video {video_id}")
            path = DATA_SOURCE.get_video_path(video_id)
            print(f"Video path: {path}")
            if not path or not os.path.exists(path):
                raise HTTPException(status_code=404, detail="Video not found")

            file_size = os.path.getsize(path)
            range_header: Optional[str] = request.headers.get("range") or request.headers.get("Range")

            start = 0
            end = file_size - 1

            if True: #range_header:
                # Parse Range: bytes=start-end
                try:
                    units, range_spec = range_header.split("=")
                    if units.strip() != "bytes":
                        raise ValueError
                    start_str, end_str = range_spec.split("-")
                    if start_str.strip():
                        start = int(start_str)
                    if end_str.strip():
                        end = int(end_str)
                except Exception:
                    # Invalid Range header
                    raise HTTPException(status_code=416, detail="Invalid Range header")

                end = min(end, file_size - 1)
                if start > end or start < 0:
                    raise HTTPException(status_code=416, detail="Invalid Range values")

                content_length = end - start + 1
                headers = {
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length),
                    "Content-Type": DATA_SOURCE.get_mime_type(video_id) or "video/mp4",
                }
                f = open(path, "rb")
                return StreamingResponse(
                    _file_iterator(f, start, end),
                    status_code=206,
                    headers=headers,
                    media_type=headers["Content-Type"],
                    background=BackgroundTask(f.close),
                )

            # No Range header: return the entire file
            headers = {
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
                "Content-Type": DATA_SOURCE.get_mime_type(video_id) or "video/mp4",
            }
            f = open(path, "rb")
            return StreamingResponse(
                _file_iterator(f, 0, file_size - 1),
                media_type=headers["Content-Type"],
                headers=headers,
                background=BackgroundTask(f.close),
            )

        self.app = app


    def __call__(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=8000)