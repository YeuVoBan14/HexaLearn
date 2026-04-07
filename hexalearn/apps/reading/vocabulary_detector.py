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
    def __init__(self):
        self._tagger = None  # ← không khởi tạo ngay

    def _get_tagger(self):
        if self._tagger is None:
            import fugashi
            self._tagger = fugashi.Tagger()
        return self._tagger

    def tokenize(self, content: str) -> set:
        tagger = self._get_tagger()
        tokens = set()
        for word in tagger(content):
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

def detect_vocabulary(paragraph, language_code=None, replace: bool = False) -> int:
    from apps.dict.models import Word

    logger.info("=== detect_vocabulary called for paragraph #%s ===", paragraph.pk)
    if not paragraph.content:
        logger.warning("Paragraph #%s has no content, skipping.", paragraph.pk)
        return 0

    if replace:
        paragraph.vocabulary.clear()

    # Lấy language_code từ passage
    if not language_code:
        if paragraph.passage and paragraph.passage.language:
            language_code = paragraph.passage.language.code
        
    logger.info(
        "Paragraph #%s — language_code: %s — content: %s",
        paragraph.pk, language_code, paragraph.content[:50]
    )

    tokenizer = get_tokenizer(language_code or 'en')
    tokens    = tokenizer.tokenize(paragraph.content)
    
    logger.info("Token count: %d | sample tokens: %s", len(tokens), list(tokens)[:10])

    if not tokens:
        logger.warning("No tokens found.")
        return 0
    
    total_words_in_db = Word.objects.count()
    logger.info("Total words in DB: %d", total_words_in_db)

    matched_words = Word.objects.filter(lemma__in=tokens)
    logger.info("Matched words: %s", list(matched_words.values_list('lemma', flat=True)))
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
    
    lang_code = passage.language.code if passage.language else 'en'
    paragraphs        = passage.paragraphs.all()
    total_words_added = 0

    for paragraph in paragraphs:
        # 4. Truyền lang_code vào đây
        total_words_added += detect_vocabulary(paragraph, language_code=lang_code, replace=replace)

    logger.info(
        "Passage #%s: %d paragraph(s), %d word(s) added.",
        passage.pk, paragraphs.count(), total_words_added
    )

    return {
        "total_paragraphs" : paragraphs.count(),
        "total_words_added": total_words_added,
    }