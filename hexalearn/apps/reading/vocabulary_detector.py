# apps/reading/vocabulary_detector.py

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# BASE
# ---------------------------------------------------------------------------

class BaseTokenizer(ABC):
    @abstractmethod
    def tokenize(self, content: str) -> set:
        pass


# ---------------------------------------------------------------------------
# TOKENIZERS
# ---------------------------------------------------------------------------

class DefaultTokenizer(BaseTokenizer):
    """Dùng cho tiếng Anh, Việt — tách theo space."""
    def tokenize(self, content: str) -> set:
        return set(content.split())


class JapaneseTokenizer(BaseTokenizer):
    """Dùng cho tiếng Nhật — dùng fugashi để tách từ và lấy lemma gốc."""
    def __init__(self):
        try:
            import fugashi
            self._tagger = fugashi.Tagger()
        except ImportError:
            raise ImportError("fugashi is required for Japanese tokenization. Run: pip install fugashi unidic-lite")

    def tokenize(self, content: str) -> set:
        tokens = set()
        for word in self._tagger(content):
            # Thêm cả dạng xuất hiện lẫn lemma gốc
            if word.surface:
                tokens.add(word.surface)
            if word.feature.lemma:
                tokens.add(word.feature.lemma)
        return tokens


# ---------------------------------------------------------------------------
# FACTORY
# ---------------------------------------------------------------------------

_TOKENIZER_MAP = {
    'ja': JapaneseTokenizer,
    'en': DefaultTokenizer,
    'vi': DefaultTokenizer,
}

def get_tokenizer(language_code: str) -> BaseTokenizer:
    """
    Trả về tokenizer phù hợp theo language_code.
    Mặc định dùng DefaultTokenizer nếu không tìm thấy.
    """
    tokenizer_class = _TOKENIZER_MAP.get(language_code, DefaultTokenizer)
    return tokenizer_class()


# ---------------------------------------------------------------------------
# DETECT
# ---------------------------------------------------------------------------

def detect_vocabulary(paragraph, replace: bool = False) -> int:
    from apps.dict.models import Word

    if not paragraph.content:
        logger.warning("Paragraph #%s has no content, skipping.", paragraph.pk)
        return 0

    if replace:
        paragraph.vocabulary.clear()

    # Lấy language_code từ passage
    language_code = None
    if paragraph.passage.language:
        language_code = paragraph.passage.language.code

    tokenizer = get_tokenizer(language_code or 'en')
    tokens    = tokenizer.tokenize(paragraph.content)

    if not tokens:
        return 0

    matched_words = Word.objects.filter(lemma__in=tokens)
    if not matched_words.exists():
        return 0

    existing_ids = set(paragraph.vocabulary.values_list('id', flat=True))
    new_words    = [w for w in matched_words if w.id not in existing_ids]

    if new_words:
        paragraph.vocabulary.add(*new_words)
        logger.info(
            "Paragraph #%s [%s]: added %d word(s).",
            paragraph.pk, language_code, len(new_words)
        )

    return len(new_words)


def detect_vocabulary_for_passage(passage, replace: bool = False) -> dict:
    paragraphs        = passage.paragraphs.all()
    total_words_added = 0

    for paragraph in paragraphs:
        total_words_added += detect_vocabulary(paragraph, replace=replace)

    logger.info(
        "Passage #%s: %d paragraph(s), %d word(s) added.",
        passage.pk, paragraphs.count(), total_words_added
    )

    return {
        "total_paragraphs" : paragraphs.count(),
        "total_words_added": total_words_added,
    }