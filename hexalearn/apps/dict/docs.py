from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiResponse, OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes


# ---------------------------------------------------------------------------
# COMMON PARAMETERS
# ---------------------------------------------------------------------------

WORD_PK_PARAM = OpenApiParameter(
    name='word_pk',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='Word ID'
)

KANJI_PK_PARAM = OpenApiParameter(
    name='kanji_pk',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='Kanji ID'
)


# ---------------------------------------------------------------------------
# PART OF SPEECH
# ---------------------------------------------------------------------------

def part_of_speech_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List part-of-speech entries',
            description='Return all part-of-speech entries. language=null means the entry is shared across all languages.',
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve part-of-speech details',
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Create a new part-of-speech entry',
            description='`code` must be unique within the same language. If language=null, the code must be globally unique.',
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update a part-of-speech entry',
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete a part-of-speech entry',
        ),
    )


# ---------------------------------------------------------------------------
# WORD
# ---------------------------------------------------------------------------

def word_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List words',
            description='Return a list of words with nested meanings, pronunciations, images, kanji_words, and examples.',
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve word details',
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Create a new word',
            description="""
Create a new word together with nested data in a single request.
All nested fields are optional.

**Image upload notes:**
1. Call `GET /auth/upload-credential/?app=dict` to get a signature
2. Upload the file to Cloudinary
3. Send the metadata (file_url, file_path, file_name, mime_type) in `word_images[]`
            """,
            examples=[
                OpenApiExample(
                    'Create word 食べる',
                    value={
                        "lemma": "食べる",
                        "language": 1,
                        "level": 1,
                        "part_of_speech": 1,
                        "meanings": [
                            {
                                "language": 3,
                                "short_definition": "eat",
                                "full_definition": "1. eat 2. make a living 3. corrode"
                            }
                        ],
                        "pronunciations": [
                            {"type": "furigana", "pronunciation": "たべる"},
                            {"type": "romaji", "pronunciation": "taberu"}
                        ],
                        "kanji_words": [
                            {"kanji": 1, "reading_in_word": "た"}
                        ],
                        "examples": [
                            {
                                "sentence": "私は毎日朝ごはんを食べる。",
                                "language": 1,
                                "translation": "I eat breakfast every day.",
                                "language_of_translation": 3
                            }
                        ],
                        "word_images": [
                            {
                                "file_url": "https://res.cloudinary.com/xxx/image/upload/dict/words/taberu.jpg",
                                "file_path": "dict/words/taberu",
                                "file_name": "taberu.jpg",
                                "mime_type": "image/jpeg",
                                "alt_text": "Illustration for 食べる",
                                "file_size": 24500
                            }
                        ]
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update basic word fields',
            description='Only lemma, language, level, and part_of_speech can be updated here. Meanings, pronunciations, images, and examples should be managed through their dedicated endpoints.',
            examples=[
                OpenApiExample(
                    'Change level',
                    value={"level": 2},
                    request_only=True,
                )
            ]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete a word',
            description='Delete the word and all related data such as meanings, pronunciations, images, and examples.',
        ),
    )


def word_suggest_schema():
    return extend_schema(
        tags=['Dictionary - Word'],
        summary='Realtime word search',
        description='Quickly search by lemma, pronunciation, or meaning. Limited to 10 results.',
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search keyword. Example: たべ, taberu, eat',
                required=True,
            ),
            OpenApiParameter(
                name='language',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Language code for returned meanings. Default: vi',
                required=False,
                examples=[
                    OpenApiExample('Vietnamese', value='vi'),
                    OpenApiExample('English', value='en'),
                ]
            ),
        ],
    )


# ---------------------------------------------------------------------------
# WORD — NESTED
# ---------------------------------------------------------------------------

def word_meaning_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List meanings of a word',
            parameters=[WORD_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve meaning details',
            parameters=[WORD_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Add a new meaning to a word',
            parameters=[WORD_PK_PARAM],
            description='Each word can have only one meaning entry per language.',
            examples=[
                OpenApiExample(
                    'Add Vietnamese meaning',
                    value={
                        "language": 3,
                        "short_definition": "eat",
                        "full_definition": "1. eat 2. make a living 3. corrode"
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update a meaning',
            parameters=[WORD_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete a meaning',
            parameters=[WORD_PK_PARAM]
        ),
    )


def word_pronunciation_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List pronunciations of a word',
            parameters=[WORD_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve pronunciation details',
            parameters=[WORD_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Add a new pronunciation',
            parameters=[WORD_PK_PARAM],
            description='Each word can have only one pronunciation per type. Furigana should only be used for Japanese words.',
            examples=[
                OpenApiExample(
                    'Add furigana',
                    value={"type": "furigana", "pronunciation": "たべる"},
                    request_only=True,
                ),
                OpenApiExample(
                    'Add romaji',
                    value={"type": "romaji", "pronunciation": "taberu"},
                    request_only=True,
                ),
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update a pronunciation',
            parameters=[WORD_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete a pronunciation',
            parameters=[WORD_PK_PARAM]
        ),
    )


def word_image_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List images of a word',
            parameters=[WORD_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve image details',
            parameters=[WORD_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Add an image to a word',
            parameters=[WORD_PK_PARAM],
            description="""
Receive metadata after the client has uploaded the file to Cloudinary/S3.

**Flow:**
1. `GET /auth/upload-credential/?app=dict` → get signature
2. Upload file to Cloudinary
3. Send file metadata to this endpoint
            """,
            examples=[
                OpenApiExample(
                    'Add image from Cloudinary',
                    value={
                        "file_url": "https://res.cloudinary.com/xxx/image/upload/dict/words/taberu.jpg",
                        "file_path": "dict/words/taberu",
                        "file_name": "taberu.jpg",
                        "mime_type": "image/jpeg",
                        "alt_text": "Illustration",
                        "file_size": 24500
                    },
                    request_only=True,
                )
            ]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete an image',
            parameters=[WORD_PK_PARAM]
        ),
    )


def word_example_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List example sentences of a word',
            parameters=[WORD_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve example sentence details',
            parameters=[WORD_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Add an example sentence to a word',
            parameters=[WORD_PK_PARAM],
            examples=[
                OpenApiExample(
                    'Add example sentence',
                    value={
                        "sentence": "私は毎日朝ごはんを食べる。",
                        "language": 1,
                        "translation": "I eat breakfast every day.",
                        "language_of_translation": 3
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update an example sentence',
            parameters=[WORD_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete an example sentence',
            parameters=[WORD_PK_PARAM]
        ),
    )


def word_kanji_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List kanji linked to a word',
            parameters=[WORD_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve Word-Kanji link details',
            parameters=[WORD_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Add kanji to a word',
            parameters=[WORD_PK_PARAM],
            examples=[
                OpenApiExample(
                    'Add Kanji 食 to 食べる',
                    value={
                        "kanji": 1,
                        "reading_in_word": "た"
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update Word-Kanji link',
            parameters=[WORD_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Remove kanji from a word',
            parameters=[WORD_PK_PARAM]
        ),
    )


# ---------------------------------------------------------------------------
# KANJI
# ---------------------------------------------------------------------------

def kanji_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='List kanji',
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Retrieve kanji details',
        ),
        create=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Create a new kanji',
            examples=[
                OpenApiExample(
                    'Create Kanji 食',
                    value={
                        "character": "食",
                        "level": 1,
                        "onyomi": "ショク, ジキ",
                        "kunyomi": "た.べる, く.う",
                        "stroke_count": 9,
                        "meanings": [
                            {"language": 3, "meaning": "eat, food"},
                            {"language": 2, "meaning": "eat, food"}
                        ],
                        "examples": [
                            {
                                "sentence": "食べ物が好きです。",
                                "language": 1,
                                "translation": "I like food.",
                                "language_of_translation": 3
                            }
                        ]
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Update kanji',
            description='Only basic fields can be updated here: character, level, onyomi, kunyomi, and stroke_count.',
        ),
        destroy=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Delete kanji',
        ),
    )


def kanji_suggest_schema():
    return extend_schema(
        tags=['Dictionary - Kanji'],
        summary='Realtime kanji search',
        description='Quickly search by character, onyomi, kunyomi, or meaning. Limited to 10 results.',
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Keyword. Example: 食, ショク, た.べる, eat',
                required=True,
            ),
            OpenApiParameter(
                name='language',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Language code for returned meanings. Default: vi',
                required=False,
            ),
        ],
    )


# ---------------------------------------------------------------------------
# KANJI — NESTED
# ---------------------------------------------------------------------------

def kanji_meaning_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='List meanings of a kanji',
            parameters=[KANJI_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Retrieve kanji meaning details',
            parameters=[KANJI_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Add a new meaning to a kanji',
            description='Each kanji can have only one meaning entry per language.',
            parameters=[KANJI_PK_PARAM],
            examples=[
                OpenApiExample(
                    'Add Vietnamese meaning',
                    value={"language": 3, "meaning": "eat, food"},
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Update a kanji meaning',
            parameters=[KANJI_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Delete a kanji meaning',
            parameters=[KANJI_PK_PARAM]
        ),
    )


def kanji_example_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='List example sentences of a kanji',
            parameters=[KANJI_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Retrieve kanji example details',
            parameters=[KANJI_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Add an example sentence to a kanji',
            parameters=[KANJI_PK_PARAM],
            examples=[
                OpenApiExample(
                    'Add example sentence',
                    value={
                        "sentence": "食べ物が好きです。",
                        "language": 1,
                        "translation": "I like food.",
                        "language_of_translation": 3
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Update an example sentence',
            parameters=[KANJI_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Delete an example sentence',
            parameters=[KANJI_PK_PARAM],
        ),
    )