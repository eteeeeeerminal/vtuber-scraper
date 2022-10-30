from dataset_for_ml_model.VideoDownloader import VideoDownloader


downloader = VideoDownloader("dataset/dataset.json", "dataset/videos")
downloader.download_dataset_videos()
