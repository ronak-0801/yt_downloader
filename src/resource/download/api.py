from fastapi import WebSocket
import asyncio
from fastapi import HTTPException, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi_socketio import SocketManager
from src.functionality.progress import ProgressTracker
from src.functionality.download import Downloader, processHookInfo
from .schema import VideoInfo, VideoUrl

router = APIRouter()
pt = ProgressTracker()


@router.post("/download")
async def downloadUrl(vidUrl: VideoUrl):
    ydl = Downloader()
    filename = ydl.getFilename(vidUrl.url)
    res = ydl.download([vidUrl.url])
    print(res)
    return filename


@router.post("/mp3")
async def downloadMp3(vidUrl: VideoUrl):
    ydl = Downloader()
    filename = ydl.getFilename(vidUrl.url)
    ydl.mp3Mode()
    res = ydl.download([vidUrl.url])
    print(res)
    return filename


@router.post("/formats")
async def formatsUrl(vidUrl: VideoUrl):
    url = vidUrl.url
    ydl = Downloader()
    info = ydl.getFormats(url)
    if info is None:
        raise HTTPException(status_code=404, detail="URL not supported")
    else:
        return info


@router.post("/info")
async def infoUrl(vidUrl: VideoUrl):
    url = vidUrl.url
    ydl = Downloader()
    info = ydl.getInfo(url)
    if info is None:
        raise HTTPException(status_code=404, detail="URL not supported")
    else:
        return VideoInfo(
            title=info["title"],
            thumbUrl=info["thumbnail"],
            site=info["webpage_url_domain"],
            url=info["webpage_url"],
        )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        event = data.get("event")

        if event == "queryprogress":
            dl_id = int(data["download_id"])
            res = {
                "status": pt.getStatus(dl_id),
                "percentage": pt.getPercentage(dl_id),
                "filename": pt.getFilename(dl_id),
            }
            await websocket.send_json({"event": f"progress.{dl_id}", "data": res})

        elif event == "download":
            dl_id = int(data["download_id"])
            url = data["url"]

            pt.attachDownload(url, dl_id)

            def temphook(d):
                pt.loadHookInfo(dl_id, processHookInfo(d))

            ydl = Downloader()

            if data.get("mp3"):
                ydl.mp3Mode()
                ext = "mp3"
            else:
                ext = None

            ydl.add_progress_hook(temphook)

            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, ydl.extract_info, url)

            ext = res["ext"] if ext is None else ext
            filename = f"{res['id']}.{res['extractor']}.{ext}"

            await websocket.send_json({"event": f"finished.{dl_id}", "data": filename})
