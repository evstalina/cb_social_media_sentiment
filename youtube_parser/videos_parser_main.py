from googleapiclient.discovery import build
import time
import pandas as pd
from datetime import datetime, timedelta
from argparse import ArgumentParser
from _videos_parser import *

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--path_dir", help="save path", dest="path", default="videos.csv")
    parser.add_argument("-k", "--key", help="API key", dest="key")
    parser.add_argument("-c", "--channelId", help="channelId", dest="channelId")
    args = parser.parse_args()
    

    youtube = build("youtube", "v3", developerKey=args.key)
    all_videos = process_channel_videos(youtube, args.channelId)

    pd.DataFrame(data = all_videos).to_csv(args.path)