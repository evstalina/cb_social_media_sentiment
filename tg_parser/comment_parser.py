import os
import time
import datetime
import pandas as pd

from _parser import *
from tqdm import tqdm
from argparse import ArgumentParser


DEFAULT_OUT_DIR = 'out_comments/'
SLEEP_SECONDS = 4

if __name__  == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--path_dir", help="Path to folder with posts files", dest="path", default="")
    parser.add_argument("-f", "--files", help="List of files with posts", dest="files", default=[], nargs='+')
    parser.add_argument("-b", "--batch", help="Size of batch to download", dest="batch", default=100)
    parser.add_argument("-a", "--accaunt_n", help="Account number to use from tg_keys, e. g. +78005553535", dest="acc_number", default="")
    args = parser.parse_args()

    if not os.path.exists(DEFAULT_OUT_DIR):
        os.mkdir(DEFAULT_OUT_DIR)
    
    client = get_client(args.acc_number)
    client.start()

    day_x = datetime.datetime(2020, 9, 22).date()

    for file_name in args.files:
        posts = pd.read_csv(args.path + "/" + file_name)
        posts["date"] = pd.to_datetime(posts["date"]).dt.date
        posts = posts[posts["date"] > day_x]
       
        comments = pd.DataFrame([])
        for post_id, channel in tqdm(zip(posts["id"], posts["channel_username"])):
            try:
                c = get_comments(client, channel, int(post_id))
            except:
                print("BAN on post [{}] channel [{}]".format(post_id, channel))
                break
            if len(c) > 0:
                comments = pd.concat([comments, c])
            time.sleep(SLEEP_SECONDS)

        if len(comments) == 0:
            print("No comments in channel [{}]".format(channel))
        else:
            comments = comments.sort_values(by=['post_id', 'date'])
            comments.to_csv("{}out_comments_{}.csv".format(DEFAULT_OUT_DIR, channel))
            print("Success {} comments parse in channel [{}]".format(len(comments), channel))
        