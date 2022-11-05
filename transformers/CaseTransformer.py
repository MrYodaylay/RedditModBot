from typing import Dict

from pipelayer import Filter

from dataclass import SubmissionContext


class CaseTransformer(Filter):

    def run(self, data: Dict, context: SubmissionContext) -> Dict:

        temp_title: str = context.get_previous("title")
        temp_selftext: str = context.get_previous("selftext")

        context.insert("case_transformer", "title", temp_title.lower())
        context.insert("case_transformer", "selftext", temp_selftext.lower())

        return data
