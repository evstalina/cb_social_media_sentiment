import os
import time
import datetime
import pandas as pd

from _parser import *
from tqdm import tqdm
from argparse import ArgumentParser

DEFAULT_OUT_DIR = 'out_posts/'
SPAN_DAY = 7
SLEEP_SECONDS = 10

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-s", "--span", help="Number of days to upload after the selected date", dest="span", default="7d")
    parser.add_argument("-d", "--dates", help="Path to csv file with dates to parce", dest="dates", default="date.csv")
    parser.add_argument("-c", "--channels", help="List of chennels to parse", dest="channels",  nargs='+', default=[])
    parser.add_argument("-a", "--accaunt_n", help="Account number to use from tg_keys, e. g. +78005553535", dest="acc_number", default="")
    parser.add_argument("-b", "--batch", help="Size of batch to download", dest="batch", default=100)
    args = parser.parse_args()
    batch = int(args.batch)

    SPAN_DAY = int(args.span[:-1])

    if not os.path.exists(DEFAULT_OUT_DIR):
        os.mkdir(DEFAULT_OUT_DIR)

    channels = args.channels
    dates = pd.to_datetime(pd.read_csv(args.dates)["date"], format='%d.%m.%Y').dt.date
    client = get_client(args.acc_number)
    client.start()

    for channel in channels:
        all_posts = pd.DataFrame([])
        for date in tqdm(dates):
            posts, num = get_posts_in_span(date, SPAN_DAY, client, channel, batch=batch)
            if num > 0:
                all_posts = pd.concat([all_posts, posts])
            time.sleep(SLEEP_SECONDS)
        
        if len(all_posts) == 0:
            print("No message in channel [{}]".format(channel))
            continue

        all_posts = all_posts.sort_values(by=['date'])
        all_posts.to_csv("{}out_posts_{}.csv".format(DEFAULT_OUT_DIR, channel))
        print("Success {} posts parse in channel [{}]".format(len(all_posts), channel))
