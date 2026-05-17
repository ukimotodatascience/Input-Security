import requests
import time


def send_to_discord(message: str, webhook_url: str):
    """Discord Webhookにメッセージを送信する"""
    response = requests.post(webhook_url, json={"content": message})
    response.raise_for_status()
    time.sleep(10)  # Discord側の制限を回避するために10秒待機
