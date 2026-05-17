import os
import sys

from src.discord_client import send_to_discord
from src.rss_service import get_items_within_hours, get_items_yesterday


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def parse_args() -> tuple[str, str, bool, str, str, int, int]:
    # openai.yml: python main.py "$FEED_URL" "$WEBHOOK_URL" "$TRANSLATE" "$NAME" "$FETCH_MODE" "$HOURS" "$DIFF_DAYS"
    feed_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("FEED_URL", "")
    webhook_url = sys.argv[2] if len(sys.argv) > 2 else os.getenv("WEBHOOK_URL", "")
    translate = parse_bool(
        sys.argv[3] if len(sys.argv) > 3 else os.getenv("TRANSLATE"),
        default=False,
    )
    name = sys.argv[4] if len(sys.argv) > 4 else os.getenv("NAME", "ニュース")
    fetch_mode = (
        (sys.argv[5] if len(sys.argv) > 5 else os.getenv("FETCH_MODE", "hours"))
        .strip()
        .lower()
    )
    hours = int(sys.argv[6] if len(sys.argv) > 6 else os.getenv("HOURS", "1"))
    diff_days = int(sys.argv[7] if len(sys.argv) > 7 else os.getenv("DIFF_DAYS", "1"))

    if not feed_url:
        raise ValueError("feed_url が指定されていません")
    if not webhook_url:
        raise ValueError("webhook_url が指定されていません")
    if fetch_mode not in {"hours", "daily"}:
        raise ValueError("FETCH_MODE は 'hours' か 'daily' を指定してください")

    if hours < 1:
        raise ValueError("HOURS は 1 以上を指定してください")

    if diff_days < 1:
        raise ValueError("DIFF_DAYS は 1 以上を指定してください")

    return feed_url, webhook_url, translate, name, fetch_mode, hours, diff_days


def translate_if_needed(text: str, enabled: bool) -> str:
    if not enabled:
        return text

    try:
        from src.translator import translate_text

        return translate_text(text)
    except Exception:
        # 翻訳ライブラリが未導入等でも、通知自体は継続する
        return text


def run():
    feed_url, webhook_url, translate, name, fetch_mode, hours, diff_days = parse_args()

    if fetch_mode == "daily":
        items = get_items_yesterday(feed_url, diff=diff_days)
    else:
        items = get_items_within_hours(feed_url, hours=hours)

    for item in items:
        title = translate_if_needed(item.title, translate)
        message = f"【{name}】\n📰{title}\n{item.url}"
        send_to_discord(message, webhook_url)
