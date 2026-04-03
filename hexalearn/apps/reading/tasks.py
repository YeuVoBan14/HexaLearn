from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def detect_vocabulary_for_passage_task(passage_id: int, replace: bool = False):
    from .models import Passage
    from .vocabulary_detector import detect_vocabulary_for_passage

    try:
        passage = (
            Passage.objects
            .select_related('language') 
            .prefetch_related('paragraphs')
            .get(pk=passage_id)
        )
        
        result = detect_vocabulary_for_passage(passage, replace=replace)
        
        logger.info("Task done for passage #%s: %s", passage_id, result)
    except Passage.DoesNotExist:
        logger.warning("Passage #%s not found.", passage_id)
        
@shared_task
def detect_vocabulary_for_paragraph_task(paragraph_id: int, replace: bool = False):
    """Detect vocabulary cho 1 paragraph đơn lẻ (dùng khi thêm paragraph vào passage có sẵn)."""
    from .models import Paragraph
    from .vocabulary_detector import detect_vocabulary
 
    try:
        paragraph = Paragraph.objects.select_related('passage__language').get(pk=paragraph_id)
        lang_code = None
        if paragraph.passage and paragraph.passage.language:
            lang_code = paragraph.passage.language.code
        count     = detect_vocabulary(paragraph, language_code=lang_code, replace=replace)
        logger.info("Task done for paragraph #%s: %d word(s) added.", paragraph_id, count)
    except Paragraph.DoesNotExist:
        logger.warning("Paragraph #%s not found.", paragraph_id)