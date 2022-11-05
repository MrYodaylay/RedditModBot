from typing import Dict

import praw.models
from pipelayer import Filter

from dataclass import SubmissionContext


class FreeKarmaFilter(Filter):

    # Karma farming filter
    subreddit_blacklist = ["FreeKarma4You",
                           "FreeKarma4All",
                           "Karma4Free",
                           "DeFreeKarma",
                           "GetKarma_Here",
                           "karmawhore",
                           "FreeKarma_ForYouAll",
                           "FreeKarma4Users",
                           "KarmaFarming4Pros",
                           "FreeKarmaChooChoo",
                           "QuotesPorn",
                           "quotes",
                           "Facts",
                           "funfacts",
                           "wholesomememes",
                           "Funnymemes",
                           "memes",
                           "meme",
                           "meirl",
                           "me_irl",
                           "absolutelynotme_irl",
                           "2meirl4meirl"]
    karma_threshold = 0.5  # maximum percentage of karma allowed from blacklisted subreddits
    post_threshold = 0.5  # maximum percentage of posts allowed from blacklisted subreddits

    def run(self, data: Dict, context: SubmissionContext) -> Dict:

        author = context.author

        passed = True
        total_karma = 0
        blacklist_karma = 0
        total_count = 0
        blacklist_count = 0

        try:
            for submission in author.submissions.top(time_filter="year", limit=100):
                if submission.subreddit.display_name in self.subreddit_blacklist:
                    blacklist_karma += submission.score
                    blacklist_count += 1
                total_karma += submission.score
                total_count += 1

            if total_karma != 0 and total_count != 0:
                passed = blacklist_karma / total_karma < self.karma_threshold \
                    or blacklist_count / total_count < self.post_threshold
            else:
                passed = True

        except Exception as e:
            print("Exception occurred in Free Karma Filter:")
            print(e)

        data["user_history"] = {
            "passed": passed,
            "total_karma": total_karma,
            "blacklist_karma": blacklist_karma,
            "total_count": total_count,
            "blacklist_count": blacklist_count
        }

        return data
