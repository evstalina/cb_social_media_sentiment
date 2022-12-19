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
    parser.add_argument("-t", "-fileter_type", help="Filter type: simple/bigramm", dest="filter", default="simple")
    parser.add_argument("-m", "-mode", help="Filter bigramm filter mode: train/filter", default="filter", dest="mode")
    parser.add_argument("-p1", default="", dest="bigramm_text1")
    parser.add_argument("-p2", default="", dest="bigramm_text2")
    args = parser.parse_args()

    if args.filter == "bigramm":
        #print()
        b = BigramFilter()
        b.train(args.bigramm_text1, args.bigramm_text2)

    else:
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
            filter_posts_ = posts[posts["matches"] == False]

            filter_posts.to_csv("{}/{}".format(DEFAULT_OUT_DIR, file_name))
            filter_posts_.to_csv("{}/neg_{}".format(DEFAULT_OUT_DIR, file_name))

            print("Success filter [{}]: apply {}/{}".format(file_name, len(filter_posts), len(posts)))
