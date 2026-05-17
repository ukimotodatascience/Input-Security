import requests
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.models import RssItem
from src.rss_parser import extract_items, extract_fields, parse_date

TOKYO_TZ = ZoneInfo("Asia/Tokyo")


def fetch_xml_root(feed_url: str) -> ET.Element:
    """RSS/Atomを取得して、XMLのルート要素を返す"""
    response = requests.get(feed_url, timeout=30)
    response.raise_for_status()
    # response.text は推定エンコーディングでデコードされるため、
    # RSSのXML宣言とズレると文字化けする場合がある。
    # バイト列をそのまま渡してXMLパーサに宣言通り解釈させる。
    return ET.fromstring(response.content)


def get_items_yesterday(feed_url: str, diff: int = 1):
    """前日分のRSS/Atomを取得して、RSSItemのリストを返す"""
    now = datetime.now(TOKYO_TZ)
    target = (now - timedelta(days=diff)).strftime("%Y%m%d")

    root = fetch_xml_root(feed_url)
    items, feed_type = extract_items(root)

    results = []
    for item in items:
        title, url, date_str = extract_fields(item, feed_type)
        date_obj = parse_date(date_str)

        if not title or not url or not date_obj:
            continue

        date_str_fmt = date_obj.astimezone(TOKYO_TZ).strftime("%Y%m%d")
        if date_str_fmt == target:
            results.append(
                RssItem(
                    title=title.strip(),
                    url=url.strip(),
                    date=date_obj,
                )
            )

    return results


def get_items_within_hours(feed_url: str, hours: int):
    """直近N時間分のRSS/Atomを取得して、RSSItemのリストを返す"""
    now = datetime.now(TOKYO_TZ)
    cutoff = now - timedelta(hours=hours)

    root = fetch_xml_root(feed_url)
    items, feed_type = extract_items(root)

    results = []
    for item in items:
        title, url, date_str = extract_fields(item, feed_type)
        date_obj = parse_date(date_str)

        if not title or not url or not date_obj:
            continue

        item_time = date_obj.astimezone(TOKYO_TZ)
        if cutoff <= item_time <= now:
            results.append(
                RssItem(
                    title=title.strip(),
                    url=url.strip(),
                    date=date_obj,
                )
            )

    return results
