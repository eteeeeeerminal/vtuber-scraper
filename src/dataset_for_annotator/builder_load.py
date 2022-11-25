from vpost.vtuber_data import VideoData

from .data_types.common import JST
from .data_types.merged import YouTubeVideoData

def videodata_to_youtube_videodata(video_data: VideoData) -> YouTubeVideoData:
    video_data.timestamp = video_data.timestamp.replace(tzinfo=JST)
    return YouTubeVideoData(
        video_data.video_id, video_data.title,
        None, video_data.timestamp
    )


