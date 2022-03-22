import os
from pprint import pprint

from dotenv import load_dotenv

from twitter import TwitterAPIWrapper


def callback(d: dict):
    if "connection_issue" in d:
        pprint(d)
        return
    data = d["data"]
    if data["lang"] == "ja":
        pprint(data)


def main(token):
    print('collect_tweet')
    twitter = TwitterAPIWrapper(token)
    twitter.sampled_stream(callback)


if __name__ == "__main__":
    load_dotenv()
    token = os.environ.get("TWITTER_BEARER_TOKE")
    main(token)
