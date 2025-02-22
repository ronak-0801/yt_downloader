from datetime import datetime
from yt_dlp import YoutubeDL
from src.resource.download.schema import FormatInfo
from yt_dlp.postprocessor.ffmpeg import FFmpegExtractAudioPP

# dict_keys(['status', 'downloaded_bytes', 'total_bytes', 'tmpfilename', 'filename', 'eta', 'speed', 'elapsed', 'ctx_id', 'info_dict', '_eta_str',
#           '_speed_str', '_percent_str', '_total_bytes_str', '_total_bytes_estimate_str', '_downloaded_bytes_str', '_elapsed_str', '_default_template'])


def processHookInfo(d):
    info = {
        "status": d.get("status"),
        "downloaded_bytes": d.get("downloaded_bytes", 0),
        "total_bytes": d.get("total_bytes", 1),
        "filename": d.get("filename", ".\\").split("\\")[-1],
    }
    return info


ydl_opts = {
    "outtmpl": "C:/Users/ronak/Downloads/ddd/%(id)s.%(extractor)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    # "proxy": "",
}


class Downloader(YoutubeDL):

    def __init__(self):
        super().__init__(ydl_opts)

    def tryInfo(self, url):
        try:
            info = self.extract_info(url, download=False)
        except:
            return None
        return info

    def getInfo(self, url):
        return self.tryInfo(url)

    def getInfoSanitized(self, url):
        info = self.tryInfo(url)
        return self.sanitize_info(info)

    def getFilename(self, url):
        info = self.tryInfo(url)
        if info is None:
            return ""
        return f"{info['id']}.{info['extractor']}.{info['ext']}"

    def getFilenameMp3(self, url):
        info = self.tryInfo(url)
        if info is None:
            return ""
        return f"{info['id']}.{info['extractor']}.mp3"

    def tryDownload(self, url):
        try:
            return self.download([url])
        except:
            return -1

    def getFormats(self, url):
        info = self.getInfo(url)
        formats = []
        if info is not None:
            for fmt in info["formats"]:
                fi = FormatInfo.parse_obj(fmt)
                formats.append(fi)
            return formats
        else:
            return None

    def pickFormat(self, format_id):
        self.format_selector = self.build_format_selector(format_id)

    def mp3Mode(self):
        self.add_post_processor(FFmpegExtractAudioPP(preferredcodec="mp3"))
