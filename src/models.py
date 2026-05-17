from dataclasses import dataclass
from datetime import datetime


@dataclass
class RssItem:
    title: str
    url: str
    date: datetime
