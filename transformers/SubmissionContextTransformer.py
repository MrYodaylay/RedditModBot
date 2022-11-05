import sqlite3
import time
from typing import Dict

from pipelayer import Filter

from dataclass import SubmissionContext


class SubmissionContextTransformer(Filter):

    def run(self, data: Dict, context: SubmissionContext) -> Dict:

        context.insert(None, "title", context.submission.title)
        context.insert(None, "selftext", context.submission.selftext)

        db = context.db
        cursor = db.cursor()

        try:
            cursor.execute("INSERT INTO posts VALUES (%s, %s, %s, %s, %s, %s)",
                           (context.submission.id,
                            context.submission.author.id,
                            context.submission.created_utc,
                            context.submission.permalink,
                            context.submission.title,
                            context.submission.selftext))
            cursor.close()
        except Exception as e:
            data["duplicate"] = True
            print("Exception occurred in Submission context transformer:")
            print(e)

        return data
