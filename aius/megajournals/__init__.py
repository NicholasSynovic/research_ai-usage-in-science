from aius.megajournals.bmj import BMJ
from aius.megajournals.f1000 import F1000
from aius.megajournals.frontiersin import FrontiersIn
from aius.megajournals.plos import PLOS

MEGAJOURNAL_MAPPING: dict[str, object] = {
    "bmj": BMJ,
    "f1000": F1000,
    "frontiersin": FrontiersIn,
    "plos": PLOS,
}
