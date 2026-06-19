"""
Листинг 3.5 — Тематическое моделирование и анализ тональности.
Соответствует коду из nn.ipynb, исправленная рабочая версия.
"""

import re
import numpy as np
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from transformers import pipeline


# ── Инициализация моделей (однократно при импорте) ────────────────────────────

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

topic_model = BERTopic(
    embedding_model=embedding_model,
    verbose=False,
    min_topic_size=2,
)

sentiment_model = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
)

# Обучающий корпус — представительная выборка тематических предложений,
# на которой BERTopic строит пространство тем перед инференсом.
_TRAIN_CORPUS = [
    "Айфон получил новый дизайн и улучшенную камеру",
    "Новый смартфон работает быстрее предыдущей версии",
    "Батарея у телефона разряжается слишком быстро",
    "Экран стал ярче и приятнее для глаз",
    "Камера делает качественные фотографии даже ночью",
    "TikTok снова набирает популярность среди пользователей",
    "Алгоритмы Instagram плохо продвигают новые посты",
    "YouTube изменил рекомендации видео",
    "Социальные сети становятся менее интересными",
    "Новый тренд в TikTok быстро стал вирусным",
    "ChatGPT помогает писать тексты и код",
    "Искусственный интеллект активно развивается",
    "Нейросети начинают заменять людей в некоторых задачах",
    "AI используется для генерации изображений",
    "Многие компании внедряют искусственный интеллект",
    "Новая игра стала популярной среди стримеров",
    "Графика в игре выглядит устаревшей",
    "Игровая индустрия растет с каждым годом",
    "Игроки жалуются на баги в новой игре",
    "Геймплей стал более интересным и динамичным",
    "Маркетинг в социальных сетях становится сложнее",
    "Реклама в интернете становится менее эффективной",
    "Бренды активно используют блогеров для продвижения",
    "Контент должен быть уникальным, чтобы привлечь внимание",
    "Алгоритмы платформ влияют на охваты",
    "Люди стали больше времени проводить в интернете",
    "Онлайн-образование становится популярнее",
    "Удаленная работа становится нормой",
    "Цифровые технологии меняют образ жизни",
    "Многие сервисы переходят в онлайн",
    "Видеоконтент становится популярнее текстового",
    "Короткие видео набирают больше просмотров",
    "Стриминг продолжает развиваться",
    "Платформы конкурируют за внимание пользователей",
    "Контент становится более персонализированным",
]

topic_model.fit(_TRAIN_CORPUS)


# ── Функции ───────────────────────────────────────────────────────────────────

def split_text(text: str) -> list[str]:
    """Разбивает текст на предложения по знакам препинания и союзам."""
    parts = re.split(r"[.!?]|но|а|однако", text)
    return [p.strip() for p in parts if p.strip()]


def analyze_text(text: str) -> dict[str, str]:
    """
    Определяет ключевые темы текста и тональность по каждой теме.

    Возвращает словарь вида:
        {"тема": "positive" | "negative" | "neutral", ...}

    Алгоритм:
        1. Разбиение текста на предложения.
        2. Векторизация и тематическая кластеризация (BERTopic).
        3. Оценка тональности каждого предложения (BERT sentiment).
        4. Взвешенное усреднение по темам, пороги ±0.2.
    """
    sentences = split_text(text)
    if not sentences:
        return {}

    topics, _ = topic_model.transform(sentences)

    # маппинг topic_id → название темы
    topic_names: dict[int, str] = {}
    for tid in set(topics):
        if tid == -1:
            topic_names[tid] = "другое"
        else:
            words = topic_model.get_topic(tid)
            topic_names[tid] = words[0][0] if words else "другое"

    topic_scores: dict[str, list[float]] = {}

    for sentence, tid in zip(sentences, topics):
        result = sentiment_model(sentence)[0]
        label: str = result["label"]
        score: float = result["score"]

        # 5-балльная шкала → [-1, 0, +1]
        if "1" in label or "2" in label:
            sent_value = -1
        elif "3" in label:
            sent_value = 0
        else:
            sent_value = 1

        topic_name = topic_names[tid]
        topic_scores.setdefault(topic_name, []).append(sent_value * score)

    result_dict: dict[str, str] = {}
    for topic, values in topic_scores.items():
        avg = np.mean(values)
        if avg > 0.2:
            result_dict[topic] = "positive"
        elif avg < -0.2:
            result_dict[topic] = "negative"
        else:
            result_dict[topic] = "neutral"

    return result_dict


# ── Пример использования ──────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = (
        "Айфон красивый, цвет очень понравился, но камера слабая, "
        "зато работает быстро. TikTok снова в тренде, алгоритмы стали лучше. "
        "Батарея разряжается слишком быстро — это огромный минус."
    )
    print(analyze_text(sample))
