import pandas as pd
import taipy.gui.builder as tgb
from taipy.gui import Icon, notify
from .transactionnews import *
from config.user import User
from typing import List


DELETE_BUTTON = Icon("images/Delete.png")
newsfeed = None


class NewsFeed:
    def __init__(self, user: User):
        self.user = user
        self.newsfeed_df: pd.DataFrame = self.get_newsfeed_df_from_user()
        self.newsfeed: list = self.get_newsfeed()

    def set_newsfeed_df_to_seen(self):
        self.newsfeed_df["unseen"] = False
        self.user.write_newsfeed(self.newsfeed_df)

    def get_number_of_unseen_news(self) -> int:
        return sum(self.newsfeed_df["unseen"])

    def get_newsfeed_df_from_user(self) -> pd.DataFrame:
        newsfeed_df = self.user.get_newsfeed()
        newsfeed_df["timestamp"] = pd.to_datetime(
            newsfeed_df["timestamp"], format="%Y-%m-%dT%H:%M:%S"
        )
        return newsfeed_df

    def get_newsfeed(self) -> List[TransactionNews]:
        self.newsfeed_df.sort_values(by="timestamp", ascending=False, inplace=True)
        newsfeed = [
            TransactionNews(
                row["sender_username"],
                row["receiver_username"],
                row["message"],
                row["metadata"],
                row["message_type"],
                row["news_id"],
                row["timestamp"],
                row["unseen"],
            )
            for _, row in self.newsfeed_df.iterrows()
        ]
        return newsfeed

    def remove_news(self, news_id: str):
        try:
            # Ensure the news_id is found before proceeding
            self.newsfeed_df = self.newsfeed_df[self.newsfeed_df["news_id"] != news_id]
            self.user.write_newsfeed(self.newsfeed_df)
            self.newsfeed_df = self.get_newsfeed_df_from_user()
            self.newsfeed = self.get_newsfeed()
        except KeyError:
            print(f"news_id {news_id} not found in the DataFrame.")

    def create_newsfeed(self) -> tgb.Page:
        with tgb.Page() as page:
            for news in self.newsfeed:
                news.create_news()
        return page