from time import sleep

from pipelayer import Pipeline
from praw import Reddit
from prawcore.exceptions import PrawcoreException
import psycopg

from config import config
from dataclass import SubmissionContext
from filters import TitleFormatFilter, NilsimsaFilter, FreeKarmaFilter, SpammingFilter
from transformers import WhitespaceTransformer, SubmissionContextTransformer, CaseTransformer, UnicodeTransformer

reddit = Reddit(
    client_id=config["authentication"]["client_id"],
    client_secret=config["authentication"]["client_secret"],
    password=config["authentication"]["password"],
    user_agent=config["authentication"]["user_agent"],
    username=config["authentication"]["username"],
)

database = psycopg.connect(
    f"postgresql"
    f"://{config['database']['username']}:{config['database']['password']}"
    f"@{config['database']['address']}:{config['database']['port']}"
    f"/{config['database']['dbname']}",
    autocommit=True
)

moderation_pipeline = Pipeline(
    [
        # Sets everything up at the beginning
        SubmissionContextTransformer,
        # Converts any unusual unicode characters to normal characters
        UnicodeTransformer,
        # Ensures that the post title matches the required format
        TitleFormatFilter,
        # Lower cases everything
        CaseTransformer,
        # Removes punctuation and newline characters
        WhitespaceTransformer,
        # Checks for similarity with previous posts
        NilsimsaFilter,
        # Checks for free karma subs
        FreeKarmaFilter,
        # Checks for too manu posts recently
        SpammingFilter,
    ]
)


def main():
    subreddit = reddit.subreddit(config["subreddit"])
    mod_queue = subreddit.mod.stream.unmoderated(skip_existing=True)

    for submission in mod_queue:
        print(f"\nProcessing post: {submission.permalink}")

        if "DirtyRedditChat" in submission.author.moderated():
            print("Moderator post. Skipping.")
            continue

        context = SubmissionContext()
        context.submission = submission
        context.author = submission.author
        context.db = database

        decision = moderation_pipeline.run({}, context)

        if "duplicate" in decision:
            print("Already seen post. Skipping.")
            return

        print(decision)

        # Title format removal
        if 'title_format' in decision and not decision['title_format']['passed']:
            message = f"Hi. Your submission has been automatically removed because it does not follow the required " \
                      f"title format. Your post should be formatted like \"Age [R4R] Title\". Our current list of " \
                      f"recognised gender codes is M, F, TM, TF, and NB.\"\n\nThis action was performed " \
                      f"automatically by a bot. If you believe a mistake has been made, please send us a mod mail " \
                      f"and your post will be reviewed by a human moderator."
            submission.mod.remove()
            submission.mod.send_removal_message(message=message)
            print("Removed:")
            print(message)

        # Duplicate post removal
        if 'nilsimsa_match' in decision and not decision['nilsimsa_match']['passed']:
            message = f"Hi. Your submission has been automatically removed because it was too similar to another " \
                      f"post from another Redditor. To prevent spam, we cannot link you to the existing post. Try " \
                      f"changing your post a bit and try again. Note: you are allowed to repost your own posts, as " \
                      f"long as all our other rules are being followed!\n\nThis action was performed automatically " \
                      f"by a bot. If you believe a mistake has been made, please send us a mod mail and your post " \
                      f"will be reviewed by a human moderator."
            submission.mod.remove()
            submission.mod.send_removal_message(message=message)
            modnote = f"Post matches existing post {decision['nilsimsa_match']['matches'][0]['permalink']} with " \
                      f"similarity {decision['nilsimsa_match']['matches'][0]['similarity']}"
            submission.mod.create_note(note=modnote)
            print("Removed:")
            print(message)
            print(modnote)

        # Free karma subreddits removal
        if 'user_history' in decision and not decision['user_history']['passed']:
            submission.mod.remove()

            message = f"Hi. Your submission has been removed because your user history does not look organic. This " \
                      f"probably is because you have been using free karma subreddits or meme subreddits. Whilst " \
                      f"plenty of real users post on these subreddits, they are also commonly targeted by bots to " \
                      f"quickly gain karma and appear more legitimate. Please get some more interactions on genuine " \
                      f"subreddits, such as for news, hobbies, etc, and then try reposting. \n\nThis action was " \
                      f"performed automatically by a bot. If you believe a mistake has been made, please send us a " \
                      f"mod mail and your post will be reviewed by a human moderator."
            submission.mod.send_removal_message(message=message)

            modnote = f"{decision['user_history']['blacklist_karma']} out of " \
                      f"{decision['user_history']['total_karma']} was from blacklisted subreddits."
            submission.mod.create_note(note=modnote)

            print("Removed:")
            print(message)
            print(modnote)

        # Spamming filter removal
        if 'spamming' in decision and not decision['spamming']['passed']:
            submission.mod.remove()
            message = f"Hi. Your submission has been removed because you made too many post to different subreddits " \
                      f"in the last ten minutes. This can sometimes be an indicator of bot activity. Please slow " \
                      f"down your post frequency and try again later.\n\nThis action was performed " \
                      f"automatically by a bot. If you believe a mistake has been made, please send us a mod mail " \
                      f"and your post will be reviewed by a human moderator."
            submission.mod.send_removal_message(message=message)

            modnote = f"Made {decision['spamming']['count']} posts in the last ten minutes. "
            submission.mod.create_note(note=modnote)

            print("Removed:")
            print(message)
            print(modnote)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"[MAIN] Exception occurred: {e}")
