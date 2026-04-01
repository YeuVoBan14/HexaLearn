"""
docs.py — drf-spectacular schema decorators for the entire reading app.
Import and apply into views.py using @extend_schema_view or @extend_schema.
"""

from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiExample, OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers as drf_serializers

# ---------------------------------------------------------------------------
# SHARED PATH PARAMETERS
# Used to fix warning "could not derive type of path parameter"
# ---------------------------------------------------------------------------

PASSAGE_PK_PARAM = OpenApiParameter(
    name='passage_pk',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='ID of Passage.',
)

PARAGRAPH_ID_PARAM = OpenApiParameter(
    name='id',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='ID of Paragraph.',
)

TRANSLATION_PK_PARAM = OpenApiParameter(
    name='translation_pk',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='ID of ParagraphTranslation.',
)

LANGUAGE_ID_PARAM = OpenApiParameter(
    name='language_id',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='ID of Language.',
)

# ---------------------------------------------------------------------------
# TOPIC
# ---------------------------------------------------------------------------

topic_schema = extend_schema_view(
    list=extend_schema(
        summary='List Topics',
        description='Retrieve all topics. Supports searching by name or code.',
        parameters=[
            OpenApiParameter(
                name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                description='Search by name or code.',
                examples=[OpenApiExample('Example', value='science')],
            ),
        ],
        tags=['Reading'],
    ),
    retrieve=extend_schema(
        summary='Topic Detail',
        tags=['Reading'],
    ),
    create=extend_schema(
        summary='Create new Topic',
        description='`code` is automatically generated from `name`. No need to provide it.',
        tags=['Reading'],
        examples=[
            OpenApiExample(
                'Request',
                value={'name': 'Science', 'color': '#FF5733'},
                request_only=True,
            ),
            OpenApiExample(
                'Response',
                value={'id': 1, 'name': 'Science', 'code': 'science', 'color': '#FF5733',
                       'created_at': '2026-01-01T00:00:00Z', 'updated_at': '2026-01-01T00:00:00Z'},
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(summary='Update Topic', tags=['Reading']),
    partial_update=extend_schema(summary='Partial update Topic', tags=['Reading']),
    destroy=extend_schema(summary='Delete Topic', tags=['Reading']),
)

# ---------------------------------------------------------------------------
# PASSAGE
# ---------------------------------------------------------------------------

passage_schema = extend_schema_view(
    list=extend_schema(
        summary='List Passages',
        description="""
Retrieve passages with multiple filter options.

**Note:**
- `language` filters by `language.code` (e.g., `ja`, `en`, `vi`) — this is the content language.
- `estimated_read_time` filters passages with time <= given value (in minutes).
        """,
        parameters=[
            OpenApiParameter(
                name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                description='Search by title or description.',
            ),
            OpenApiParameter(
                name='language', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                description='Filter by language code. Example: `ja`, `en`, `vi`.',
                examples=[OpenApiExample('Japanese', value='ja')],
            ),
            OpenApiParameter(
                name='level', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                description='Filter by level code.',
            ),
            OpenApiParameter(
                name='topic', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                description='Filter by topic code.',
            ),
            OpenApiParameter(
                name='estimated_read_time', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                description='Filter passages with read time <= value (minutes).',
            ),
        ],
        tags=['Reading'],
    ),
    retrieve=extend_schema(
        summary='Passage Detail',
        description='Returns passage with all paragraphs and translations.',
        tags=['Reading'],
    ),
    create=extend_schema(
        summary='Create Passage',
        description="""
Create passage with paragraphs and translations in one request.

**`language`**: ID of Language — determines tokenizer:
- `ja` → JapaneseTokenizer (fugashi)
- `en`, `vi` → DefaultTokenizer

**`translation_language`**: Language ID for all paragraph translations.

**Rules:**
- Paragraph with `translation` → use provided text.
- Without or `null` → auto placeholder: `"No translation in {language} yet"`.
- After creation, Celery task auto detects vocabulary.
        """,
        tags=['Reading'],
    ),
    update=extend_schema(
        summary='Update Passage',
        description='Only updates basic info. Use `/paragraphs/` for paragraphs.',
        tags=['Reading'],
    ),
    partial_update=extend_schema(
        summary='Partial update Passage',
        tags=['Reading'],
    ),
    destroy=extend_schema(
        summary='Delete Passage',
        description='Deletes passage and all related paragraphs + translations (CASCADE).',
        tags=['Reading'],
    ),
)

detect_vocabulary_schema = extend_schema(
    summary='Run Vocabulary Detection',
    description="""
Dispatch Celery task to detect vocabulary.

- `replace = false`: add new words only.
- `replace = true`: clear old words and re-detect.

Async task, returns `202 Accepted`.
    """,
    tags=['Reading'],
)

add_translation_schema = extend_schema(
    summary='Add Translations',
    description="""
Bulk create/update translations.

Rules:
- Provide `{index, translation}`
- Missing → placeholder
- Existing → update
    """,
    tags=['Reading'],
)

remove_language_translation_schema = extend_schema(
    summary='Remove Language Translations',
    description="""
Permanently deletes all translations of a language in passage.
    """,
    parameters=[LANGUAGE_ID_PARAM],
    tags=['Reading'],
)

# ---------------------------------------------------------------------------
# PARAGRAPH
# ---------------------------------------------------------------------------

paragraph_schema = extend_schema_view(
    list=extend_schema(
        summary='List Paragraphs',
        parameters=[PASSAGE_PK_PARAM],
        tags=['Reading'],
    ),
    retrieve=extend_schema(
        summary='Paragraph Detail',
        parameters=[PASSAGE_PK_PARAM, PARAGRAPH_ID_PARAM],
        tags=['Reading'],
    ),
    create=extend_schema(
        summary='Create Paragraph',
        description="""
- Auto index
- Auto detect vocabulary
- Auto create placeholder translations
        """,
        parameters=[PASSAGE_PK_PARAM],
        tags=['Reading'],
    ),
    update=extend_schema(
        summary='Update Paragraph',
        description="""
If content changes → re-run vocabulary detection.
        """,
        parameters=[PASSAGE_PK_PARAM, PARAGRAPH_ID_PARAM],
        tags=['Reading'],
    ),
    partial_update=extend_schema(
        summary='Partial update Paragraph',
        parameters=[PASSAGE_PK_PARAM, PARAGRAPH_ID_PARAM],
        tags=['Reading'],
    ),
    destroy=extend_schema(
        summary='Delete Paragraph',
        description="""
Deletes and reorders index automatically.
        """,
        parameters=[PASSAGE_PK_PARAM, PARAGRAPH_ID_PARAM],
        tags=['Reading'],
    ),
)

reorder_schema = extend_schema(
    summary='Reorder Paragraph',
    description="""
Move paragraph to new position, others adjust automatically.
    """,
    parameters=[PASSAGE_PK_PARAM, PARAGRAPH_ID_PARAM],
    tags=['Reading'],
)

translations_list_schema = extend_schema(
    summary='List Translations',
    parameters=[PASSAGE_PK_PARAM, PARAGRAPH_ID_PARAM],
    tags=['Reading'],
)

translation_update_schema = extend_schema(
    summary='Update Translation',
    description='Only update text. Cannot change language.',
    parameters=[PASSAGE_PK_PARAM, PARAGRAPH_ID_PARAM, TRANSLATION_PK_PARAM],
    tags=['Reading'],
)

translation_delete_schema = extend_schema(
    summary='Reset Translation to Placeholder',
    description="""
Does NOT delete record — only reset text to placeholder.
    """,
    parameters=[PASSAGE_PK_PARAM, PARAGRAPH_ID_PARAM, TRANSLATION_PK_PARAM],
    tags=['Reading'],
)