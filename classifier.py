"""
classifier.py
--------------
Improved multi‑task classifier for BrandPulse Watchdog.

• Sentiment (positive / negative)      – DistilBERT SST‑2
• Emotion  (anger, joy, sadness, …)    – DistilBERT emotion model
• Type     (complaint, request, …)     – Zero‑shot with rule‑based shortcuts
• Urgency  (low / medium / high)       – Heuristic on sentiment + keywords
"""

from transformers import pipeline

# --- Pipelines -------------------------------------------------------------

SENT = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

EMO = pipeline(
    "text-classification",
    model="bhadresh-savani/distilbert-base-uncased-emotion",
    top_k=None           # return all classes with scores
)

ZSC = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

# --- Heuristic keyword sets -----------------------------------------------

CANDIDATE_TYPES   = ["complaint", "request", "question", "praise", "bug_report"]
CANDIDATE_URGENCY = ["low", "medium", "high"]

NEGATIVE_HINTS = {
    "refund", "unacceptable", "delay", "no response",
    "cold", "crashing", "rude", "missing", "cancel"
}

PRAISE_HINTS = {
    "thanks", "thank you", "great", "well done", "perfect",
    "awesome", "fantastic", "love", "excellent", "good job"
}

HIGH_URGENCY_WORDS = {
    "refund", "asap", "immediately", "urgent", "now", "unacceptable", "cancel"
}

# --- Main classifier -------------------------------------------------------


def classify(text: str) -> dict:
    """
    Classify a single support message.

    Returns dict:
        sentiment, emotion, type, urgency, confidence
    """
    lt = text.lower()

    # 1. Sentiment polarity
    sent_result = SENT(text, truncation=True, max_length=128)[0]
    sentiment   = sent_result["label"].lower()

    # 2. Emotion
    emo_all = EMO(text, truncation=True, max_length=128)
    if isinstance(emo_all[0], list):      # sometimes HF nests list-in-list
        emo_all = emo_all[0]
    top_emotion = max(emo_all, key=lambda x: x["score"])
    emotion     = top_emotion["label"].lower()
    conf        = round(top_emotion["score"], 3)

    # Override if obvious negative keywords present
    if any(kw in lt for kw in NEGATIVE_HINTS):
        sentiment = "negative"
        if emotion not in {"anger", "sadness", "fear"}:
            emotion = "anger"

    # 3. Message type
    if any(kw in lt for kw in PRAISE_HINTS):
        msg_type = "praise"
    elif "?" in text and sentiment == "positive":
        msg_type = "question"
    elif any(kw in lt for kw in {"refund", "cancel", "escalate"}):
        msg_type = "complaint"
    else:
        zsc = ZSC(text, candidate_labels=CANDIDATE_TYPES)
        msg_type = zsc["labels"][0]

    # 4. Urgency
    if sentiment == "negative" and any(kw in lt for kw in HIGH_URGENCY_WORDS):
        urgency = "high"
    elif sentiment == "negative":
        urgency = "medium"
    else:
        urgency = "low"

    return {
        "sentiment":  sentiment,
        "emotion":    emotion,
        "type":       msg_type,
        "urgency":    urgency,
        "confidence": conf,
    }
