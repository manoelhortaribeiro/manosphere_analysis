from sqlitedict import SqliteDict
import datetime
import argparse
import json


parser = argparse.ArgumentParser(description="""This script generates two sqlite files that help throughout the analysis
                                                of the comments!""")

parser.add_argument("--src", dest="src", action="append",
                    help=".ndjson file with comments.")

parser.add_argument("--author_dict", dest="author_dict", action="store_true",
                    help="If present, runs author_dict, otherwise, runs for channel_dict.")

parser.add_argument("--kind", dest="kinds", action="append",
                    help="(all|random|gaming)")

parser.add_argument("--dst", dest="dst", default="/data/incels_helpers/",
                    help="If present, runs author_dict, otherwise, runs for channel_dict.")

args = parser.parse_args()

dst = args.dst + "authors_dict.sqlite" if args.author_dict else args.dst + "channels_dict.sqlite"
table_name = "authors" if args.author_dict else "channels"
dict_db = SqliteDict(dst, tablename=table_name, journal_mode="OFF")
tmp_dict = dict()

fs = [open(f, "r") for f in args.src]
kinds = [k for k in args.kinds]

count = 0
now = datetime.datetime.now()

for f, k in zip(fs, kinds):
    print("---->", k)
    for line in f:

        count += 1
        line = json.loads(line)

        if args.author_dict:  # -- updates authors_dict
            author = line["author"]
            dict_val = {
                        "timestamp": int(line["created_utc"]),
                        "subreddit": line["subreddit"].lower() if k == "all" else k,
                        "id": line["id"]
                        }
            val = tmp_dict.get(author, [])
            val.append(dict_val)
            tmp_dict[author] = val

        else:  # -- updates channel_dict
            subreddit = line["subreddit"].lower() if k == "all" else k
            dict_val = {
                        "author": line["author"],
                        "timestamp": int(line["created_utc"]),
                        }
            val = tmp_dict.get(subreddit, [])
            val.append(dict_val)
            tmp_dict[subreddit] = val

        if count % 2500000 == 0:

            for key, item in tmp_dict.items():
                try:
                    val = dict_db.get(key, [])
                    val += item
                    dict_db[key] = val
                except AttributeError:
                    print("AttributeError", key)
                    continue

            dict_db.commit()
            tmp_dict = {}
            print(datetime.datetime.now() - now)
            now = datetime.datetime.now()

    for key, item in tmp_dict.items():
        try:
            val = dict_db.get(key, [])
            val += item
            dict_db[key] = val
        except AttributeError:
            print("AttributeError", key)
            continue
        print(datetime.datetime.now() - now)
        now = datetime.datetime.now()
    dict_db.commit()
dict_db.close()
