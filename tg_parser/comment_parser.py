import os
import time
import datetime
import pandas as pd

from parser import *
from tqdm import tqdm

DEFAULT_OUT_DIR = 'out_comments/'
SLEEP_SECONDS = 10

if __name__  == "__main__":
    if not os.path.exists(DEFAULT_OUT_DIR):
        os.mkdir(DEFAULT_OUT_DIR)
        
    posts = pd.read_csv("out_moscowmap.csv")
    
    client = get_client()
    client.start()

    comments = pd.DataFrame([])
    for post_id, channel in tqdm(zip(posts["id"], posts["channel_username"])):
        c = get_comments(client, channel, post_id)
        if len(c) > 0:
            comments = pd.concat([comments, c])
        break
        time.sleep(SLEEP_SECONDS)

    if len(comments) == 0:
        print("No comments in channel [{}]".format(channel))
    else:
        comments = comments.sort_values(by=['post_id', 'date'])
        comments.to_csv("{}out_comments_{}.csv".format(DEFAULT_OUT_DIR, channel))
        print("Success {} comments parse in channel [{}]".format(len(comments), channel))