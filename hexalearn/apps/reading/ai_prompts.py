# PROMPT TEMPLATE FOR READING EXPLANINER AI

# ---------------------------------------------------------------------------
# SYSTEM INSTRUCTION — widely used for all interactions with the AI, sets the overall behavior and guidelines
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """
You are an expert language teacher specializing in helping learners understand 
reading passages. You are knowledgeable in Japanese, Vietnamese, and English.
 
Rules:
- Always respond in the user's native language unless showing target language examples
- Be concise but thorough
- Use simple, clear explanations suitable for the learner's level
- Always include the original Japanese when referencing specific words or phrases
- Format your response clearly with sections when appropriate
"""

# ---------------------------------------------------------------------------
# EXPLAIN — explain grammar and vocabulary in a selected text
# ---------------------------------------------------------------------------

EXPLAIN_PROMPT = """
## Context
The student is reading a passage in {passage_language}.
Their level: {level}
Their native language: {native_language}
 
## Full paragraph (for context only):
{full_paragraph}
 
## Selected text the student wants explained:
"{selected_text}"
 
## Task
Explain the selected text in {native_language}. Include:
 
1. **Overall meaning** — what does this mean naturally?
2. **Grammar breakdown** — explain each grammar point used
3. **Vocabulary** — list key words with reading (furigana) and meaning
4. **Nuance** — any cultural context or nuance worth noting?
 
Keep explanations appropriate for a {level} level learner.
Do NOT translate word by word — explain the natural meaning in context.
"""

# ---------------------------------------------------------------------------
# SUMMARIZE — summarize the main point of a paragraph
# ---------------------------------------------------------------------------

SUMMARIZE_PROMPT = """
## Context
The student is reading a passage in {passage_language}.
Their level: {level}
Their native language: {native_language}
 
## Paragraph to summarize:
{full_paragraph}
 
## Task
In {native_language}, provide:
 
1. **Main idea** (1-2 sentences) — what is this paragraph about?
2. **Key points** (bullet list) — 3-5 important points from the paragraph
3. **Vocabulary highlight** — 3 most important words to remember:
   - Word (with furigana if applicable)
   - Meaning in {native_language}
   - Why it's important in this context
"""

# ---------------------------------------------------------------------------
# VOCABULARY — list and explain hard vocabulary
# Use when user want to listed and understand hard vocabulary in a selected text
# ---------------------------------------------------------------------------

VOCABULARY_PROMPT = """
## Context
The student is a {level} level {passage_language} learner.
Their native language: {native_language}
 
## Text to analyze:
"{selected_text}"
 
## Full paragraph context:
{full_paragraph}
 
## Task
List ALL vocabulary worth learning from the selected text.
For each word provide in {native_language}:
 
| Word | Reading | Meaning | JLPT | Difficulty |
|------|---------|---------|------|------------|
 
After the table, for the TOP 3 most important words, add:
- A natural example sentence (in {passage_language})
- Translation of the example sentence
- A memory tip
 
Focus on words that are:
- Not basic/elementary (skip words like は、が、の)
- Useful for {level} level learners
- Relevant to understanding the passage
"""

# ---------------------------------------------------------------------------
# BUILDER FUNCTIONS
# Nhận paragraph object + request params → trả về prompt string
# ---------------------------------------------------------------------------

def build_explain_prompt(paragraph, selected_text: str, user) -> tuple[str, str]:
    context = _build_context(paragraph, user)
    prompt  = EXPLAIN_PROMPT.format(
        selected_text = selected_text or paragraph.content,
        **context,
    )
    return prompt

def build_summarize_prompt(paragraph, user) -> tuple[str, str]:
    context = _build_context(paragraph, user)
    prompt = SUMMARIZE_PROMPT.format(**context)
    return prompt

def build_vocabulary_prompt(paragraph, selected_text: str, user) -> tuple[str, str]:
    context = _build_context(paragraph, user)
    prompt = VOCABULARY_PROMPT.format(
        selected_text = selected_text or paragraph.content,
        **context,
    )
    return prompt

def _build_context(paragraph, user) -> dict:
    passage_language = '	Japanese'
    if paragraph.passage.language:
        passage_language = paragraph.passage.language.name
 
    native_language = 'Vietnamese'
    try:
        if user.profile.native_language:
            native_language = user.profile.native_language.name
    except Exception:
        pass
 
    level = 'N5 Beginner'
    try:
        if user.profile.reading_level:
            level = user.profile.reading_level.name
    except Exception:
        pass
 
    return {
        'passage_language': passage_language,
        'native_language' : native_language,
        'level'           : level,
        'full_paragraph'  : paragraph.content,
    }


