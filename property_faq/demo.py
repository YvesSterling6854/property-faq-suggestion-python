import json
import sys

from .infrai_gateway import InfraiGateway
from .service import FaqQuery, FaqSuggestionService


def main() -> None:
    text = " ".join(sys.argv[1:]) or "How do I report a repair?"
    entries = FaqSuggestionService(InfraiGateway()).suggest(FaqQuery(text))
    print(json.dumps([e.__dict__ for e in entries], indent=2))


if __name__ == "__main__":
    main()

