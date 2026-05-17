from datetime import datetime
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET


def extract_items(root: ET.Element):
    """RSS/Atomのルート要素から、item要素を抽出して、feed_typeを返す"""
    if root.tag.endswith("feed"):
        return [c for c in root if c.tag.endswith("entry")], "atom"

    channel = root.find("channel")
    if channel is not None:
        return channel.findall("item"), "rss"

    return [c for c in root if c.tag.endswith("item")], "rss"


def extract_fields(item: ET.Element, feed_type: str):
    """item要素から、title, url, dateを抽出して、返す"""
    if feed_type == "atom":
        title = get_text(item, "title")
        url = get_atom_link(item)
        date_str = get_text(item, ["published", "updated"])
    else:
        title = get_text(item, ["title", "dc:title"])
        url = get_text(item, ["link", "guid"])
        date_str = get_text(item, ["pubDate", "dc:date", "published", "date"])

    return title, url, date_str


def get_text(item: ET.Element, tags):
    """item要素から、textを抽出して、返す"""
    if isinstance(tags, list):
        for tag in tags:
            value = get_text(item, tag)
            if value:
                return value
        return ""

    tag_suffix = tags.split(":")[-1]

    for child in item:
        if child.tag.endswith(tag_suffix):
            return (child.text or "").strip()

    return ""


def get_atom_link(item: ET.Element) -> str:
    """item要素から、atom:link要素を抽出して、hrefを返す"""
    links = [c for c in item if c.tag.endswith("link")]
    if not links:
        return ""

    link_elem = links[0]
    for link in links:
        if link.attrib.get("rel") == "alternate":
            link_elem = link
            break

    return link_elem.attrib.get("href", "").strip()


def parse_date(date_str: str):
    """date_strをdatetimeに変換して、返す"""
    if not date_str:
        return None

    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None
