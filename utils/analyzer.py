from collections import Counter
import hashlib

from model import AnalysisResponse, AnalysisProperties


def analyze_string(value: str) -> AnalysisProperties:
    normalized = value.lower()
    freq = Counter(normalized)

    return AnalysisProperties (
        length=len(value),
        word_count= len(value.split()),
        is_palindrome= normalized == normalized[::-1],
        unique_characters=len((set(normalized))),
        sha256_hash=hashlib.sha256(value.encode()).hexdigest(),
        character_frequency_map=dict(freq)
    )