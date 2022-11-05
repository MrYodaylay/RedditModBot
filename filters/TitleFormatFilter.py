import re
from typing import Dict

from pipelayer import Filter

from dataclass import SubmissionContext


class TitleFormatFilter(Filter):
    
    age_regex = r"((?:[1-9][0-9].?)+)"
    r4r_regex = r"((?:M|F|T|TM|TF|MTF|FTM|A|NB|R|FB)+)4((?:M|F|T|TM|TF|MTF|FTM|A|NB|R|FB)+)"
    title_regex = r"(?:(?:[1-9][0-9].?)+)\s*(?:\[)?(?:(?:M|F|T|TM|TF|MTF|FTM|A|NB|R|FB)+)4(?:(?:M|F|T|TM|TF|MTF|FTM|A|NB|R|FB)+)(?:\])?\s?(.*)"

    def run(self, data: Dict, context: SubmissionContext) -> Dict:

        age_compiled = re.compile(self.age_regex, re.IGNORECASE | re.VERBOSE)
        age_match = age_compiled.search(context.get_previous("title"))

        r4r_compiled = re.compile(self.r4r_regex, re.IGNORECASE | re.VERBOSE)
        r4r_match = r4r_compiled.search(context.get_previous("title"))

        title_compiled = re.compile(self.title_regex, re.IGNORECASE | re.VERBOSE)
        title_match = title_compiled.search(context.get_previous("title"))

        data["title_format"] = {
            "passed": age_match is not None and r4r_match is not None,
            "age": age_match.group(0) if age_match is not None else "",
            "r4r": r4r_match.group(0) if r4r_match is not None else "",
            "title": title_match.group(1) if title_match is not None else ""
        }

        return data

