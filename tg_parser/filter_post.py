import os
import pandas as pd

from _filter import *
from tqdm import tqdm
from argparse import ArgumentParser

DEFAULT_OUT_DIR = "out_posts_filter/"

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--path_dir", help="Path to folder with posts files", dest="path", default="")
    parser.add_argument("-f", "--files", help="List of files with posts", dest="files", default=[], nargs='+')
    parser.add_argument("-w", "--words_filter", help="File with filter list: level, word", dest="filter_path", default="filter_words.csv")
    args = parser.parse_args()

    if not os.path.exists(DEFAULT_OUT_DIR):
        os.mkdir(DEFAULT_OUT_DIR)
    filter_ = SimpleFilter(args.filter_path)

    for file_name in args.files:
        posts = pd.read_csv(args.path + "/" + file_name)
        matches = []
        for text in posts["text"]:
            matches.append(filter_.match(text))
        posts["matches"] = matches
        filter_posts = posts[posts["matches"]]

        filter_posts.to_csv("{}/{}".format(DEFAULT_OUT_DIR, file_name))
        print("Success filter [{}]: apply {}/{}".format(file_name, len(filter_posts), len(posts)))
