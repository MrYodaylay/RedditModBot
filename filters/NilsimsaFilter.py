import difflib
from typing import Dict

import unicodedata
import sqlite3
from nilsimsa import Nilsimsa
from pipelayer import Filter

from dataclass import SubmissionContext


def _ratio(a: str, b: str):
    return difflib.SequenceMatcher(None, a, b).ratio()


class NilsimsaFilter(Filter):

    match_threshold = 0.7

    def run(self, data: Dict, context: SubmissionContext) -> Dict:

        title = context.get_previous("title")
        selftext = context.get_previous("selftext")
        merged = title + selftext

        n1 = Nilsimsa(merged)
        digest = n1.hexdigest()

        # Search for this hash in the database
        try:
            cursor = context.db.cursor()
            cursor.execute("SELECT p.permalink, similarity(n.hash, %s) AS similarity "
                           "FROM nilsimsa n "
                           "INNER JOIN posts p "
                           "ON n.post_id = p.post_id "
                           "WHERE p.author_id != %s AND similarity(n.hash, %s) > %s;",
                           (digest, context.author.id, digest, self.match_threshold))
            results = cursor.fetchall()
        except Exception as e:
            print("Exception occurred in Nilsimsa filter:")
            print(e)
            results = True

        # Then add this one for later
        try:
            cursor.execute("INSERT INTO nilsimsa VALUES (%s, %s);",
                           (context.submission.id, digest))
        except Exception as e:
            print("Exception occurred in Nilsimsa filter:")
            print(e)

        data["nilsimsa_match"] = {
            "passed": len(results) == 0,
            "matches": []
        }

        for match in results:
            data["nilsimsa_match"]["matches"].append({
                "permalink": match[0],
                "similarity": match[1]
            })

        return data


