from deep_translator import GoogleTranslator


def translate_text(text: str) -> str:
    """取得したタイトルを日本語訳する"""
    return GoogleTranslator(source="auto", target="ja").translate(text)
