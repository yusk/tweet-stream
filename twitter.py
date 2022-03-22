import json

import requests


class TwitterAPIRequestError(Exception):
    pass


class TwitterAPIWrapper:
    API_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token):
        self.bearer_token = bearer_token

    def _get_headers(self):
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        return headers

    def _req(self, method, url, headers=None, data=None, succeeded_status=200):
        if headers is None:
            headers = self._get_headers()
        params = {
            "method": method,
            "url": url,
            "headers": headers,
        }
        if data:
            params["json"] = data
        print(params)
        res = requests.request(**params)
        if res.status_code != succeeded_status:
            raise TwitterAPIRequestError(
                f"Request returned an error: {res.status_code} {res.text}")
        return res.json()

    def _stream(self, method, url, callback, headers=None):
        if headers is None:
            headers = self._get_headers()
        try:
            res = requests.request(method, url, headers=headers, stream=True)
            for text in res.iter_lines():
                if text:
                    data = json.loads(text)
                    callback(data)
        except Exception as e:
            print(e)
            raise e
        if res.status_code != 200:
            raise TwitterAPIRequestError(
                f"Request returned an error: {res.status_code} {res.text}")
        return res

    def _get_url(self, endpoint, queries=None):
        url = f"{self.API_URL}/{endpoint}"
        if type(queries) == dict:
            query_strs = []
            for k, v in queries.items():
                if type(v) == list:
                    v = ",".join([str(x) for x in v])
                query_strs.append(f"{k}={v}")
            url += f"?{'&'.join(query_strs)}"
        return url

    def get_tweets(self, ids, tweet_fields=["lang", "author_id"]):
        """
        https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets
        """
        queries = {
            "ids": ids,
            "tweet.fields": tweet_fields,
        }
        url = self._get_url("tweets", queries=queries)
        return self._req("get", url)

    def search_tweets(
        self,
        query,
        tweet_fields=["author_id"],
        expansions=["in_reply_to_user_id", "referenced_tweets.id"],
    ):
        """
        https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent
        """
        queries = {
            "query": query,
            "tweet.fields": tweet_fields,
            "expansions": expansions
        }
        url = self._get_url("tweets/search/recent", queries=queries)
        return self._req("get", url)

    def get_users(self, usernames, user_fields=["description", "created_at"]):
        """
        https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users-by
        """
        queries = {
            "usernames": usernames,
            "user.fields": user_fields,
        }
        url = self._get_url("users/by", queries=queries)
        return self._req("get", url)

    def get_rules(self):
        url = self._get_url("tweets/search/stream/rules")
        return self._req("get", url)

    def set_rules(self, rules):
        data = {"add": rules}
        url = self._get_url("tweets/search/stream/rules")
        return self._req("post", url, data=data, succeeded_status=201)

    def set_rule(self, value, tag):
        return self.set_rules([{"value": value, "tag": tag}])

    def delete_rules(self, ids):
        data = {"delete": {"ids": ids}}
        url = self._get_url("tweets/search/stream/rules")
        return self._req("post", url, data=data)

    def sampled_stream(self,
                       callback,
                       expansions=[
                           "referenced_tweets.id",
                           "referenced_tweets.id.author_id",
                           "attachments.media_keys"
                       ],
                       tweet_fields=[
                           "id", "author_id", "text", "lang", "public_metrics",
                           "created_at"
                       ],
                       user_fields=["id", "name", "public_metrics"],
                       media_fields=["url"]):
        """
        https://developer.twitter.com/en/docs/twitter-api/tweets/sampled-stream/api-reference/get-tweets-sample-stream
        """
        queries = {
            "expansions": expansions,
            "tweet.fields": tweet_fields,
            "user.fields": user_fields,
            "media.fields": media_fields,
        }
        url = self._get_url("tweets/sample/stream", queries)
        self._stream("get", url, callback)

    def filtered_stream(
        self,
        callback,
        tweet_fields=["id", "text", "lang"],
    ):
        queries = {
            "tweet.fields": tweet_fields,
        }
        url = self._get_url("tweets/search/stream", queries)
        self._stream("get", url, callback)
