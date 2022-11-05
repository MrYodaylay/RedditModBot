from typing import Any

import psycopg.connection
from pipelayer import Context
from praw.reddit import Submission, Redditor


class SubmissionContext(Context):
    submission: Submission
    author: Redditor

    db: psycopg.Connection

    data = {
    }
    previous = {
    }

    def has(self, key: str) -> bool:
        return key in self.data

    def insert(self, stage: str, key: str, value: any):
        if stage is None:
            stage = "none"

        if not self.has(stage):
            self.data[stage] = {}

        self.data[stage][key] = value
        self.previous[key] = stage

    def get_previous(self, key: str) -> Any:
        if key in self.previous:
            return self.data[self.previous[key]][key]
        else:
            return None
