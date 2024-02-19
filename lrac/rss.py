from pprint import pprint

import feedparser
from feedparser.util import FeedParserDict

feed: FeedParserDict = feedparser.parse(
    url_file_stream_or_string="https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=signaling",
)

for e in feed["entries"]:
    print(e["dc_identifier"], e["link"])
