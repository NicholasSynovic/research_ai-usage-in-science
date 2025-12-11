from aius.search.bmj import BMJ
from aius.search.f1000 import F1000
from aius.search.frontiersin import FrontiersIn
from aius.search.plos import PLOS

MEGAJOURNAL_MAPPING: dict[str, object] = {
    "bmj": BMJ,
    "f1000": F1000,
    "frontiersin": FrontiersIn,
    "plos": PLOS,
}
