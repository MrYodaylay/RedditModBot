"""
Removes punctuation and strange whitespaces characters from the title and the selftext
"""

import string
from typing import Dict

from pipelayer import Filter

from dataclass import SubmissionContext


class WhitespaceTransformer(Filter):

    whitespace = "\t\n\r\v\f"
    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~’"""

    def run(self, data: Dict, context: SubmissionContext) -> Dict:

        temp_title: str = context.get_previous("title")
        temp_selftext: str = context.get_previous("selftext")

        for c in self.whitespace:
            temp_title = temp_title.replace(c, ' ')
            temp_selftext = temp_selftext.replace(c, ' ')

        for c in self.punctuation:
            temp_title = temp_title.replace(c, '')
            temp_selftext = temp_selftext.replace(c, '')

        temp_title = temp_title.strip()
        temp_selftext = temp_selftext.strip()

        context.insert("whitespace_transformer", "title", temp_title)
        context.insert("whitespace_transformer", "selftext", temp_selftext)

        return data
