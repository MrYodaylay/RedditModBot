import time
from typing import Dict

import praw.models
from pipelayer import Filter

from dataclass import SubmissionContext


class SpammingFilter(Filter):

    time_threshold = 600  # 10 minutes * 60 seconds = 600
    time_limit = 5  # maximum number of posts allowed in time threshold

    def run(self, data: Dict, context: SubmissionContext) -> Dict:

        author = context.author

        passed = True
        count_posts = 0

        try:
            for submission in author.submissions.new(limit=10):
                if submission.created_utc > time.time() - self.time_threshold:
                    count_posts += 1
            passed = count_posts < self.time_limit

        except Exception as e:
            print("Exception occurred in Spamming Filter:")
            print(e)
            passed = True

        data["spamming"] = {
            "passed": passed,
            "count": count_posts
        }

        return data
