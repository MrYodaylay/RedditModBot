import difflib
from typing import Dict

import unicodedata
from pipelayer import Filter

from dataclass import SubmissionContext


class UnicodeTransformer(Filter):

    title_match_fail_weight = 10
    selftext_match_fail_weight = 10

    def run(self, data: Dict, context: SubmissionContext) -> Dict:
        dirty_title = context.get_previous("title")
        clean_title = unicodedata.normalize("NFKC", dirty_title)
        context.insert("unicode_filter", "title", clean_title)

        dirty_selftext = context.get_previous("selftext")
        clean_selftext = unicodedata.normalize("NFKC", dirty_selftext)
        context.insert("unicode_filter", "selftext", clean_selftext)

        combined_clean = clean_title + clean_selftext
        combined_dirty = dirty_title + dirty_selftext

        return data
