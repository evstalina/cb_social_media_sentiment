import os
import time
import datetime
import pandas as pd

from parser import *
from tqdm import tqdm

DEFAULT_OUT_DIR = 'out_posts/'
SPAN_DAY = 7
SLEEP_SECONDS = 10

if __name__ == "__main__":
    if not os.path.exists(DEFAULT_OUT_DIR):
        os.mkdir(DEFAULT_OUT_DIR)

    channels = pd.read_csv("channels.csv")["channels"]
    dates = pd.to_datetime(pd.read_csv("date.csv")["date"], format='%d.%m.%Y').dt.date
    client = get_client()
    client.start()

    for channel in channels:
        all_posts = pd.DataFrame([])
        for date in tqdm(dates):
            posts, num = get_posts_in_span(date, SPAN_DAY, client, channel, batch=100)
            if num > 0:
                all_posts = pd.concat([all_posts, posts])
            time.sleep(SLEEP_SECONDS)
        
        if len(all_posts) == 0:
            print("No message in channel [{}]".format(channel))
            continue

        all_posts = all_posts.sort_values(by=['date'])
        all_posts.to_csv("{}out_posts_{}.csv".format(DEFAULT_OUT_DIR, channel))
        print("Success {} posts parse in channel [{}]".format(len(all_posts), channel))
