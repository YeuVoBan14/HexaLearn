from django.db import models
from django.forms import ValidationError
from apps.home.models import Language, Level, MediaFile
from django.db.models import Max
# Create your models here.

class PartOfSpeech(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('code', 'language')
        constraints = [
            # When language is null, code should be unique across all languages
            models.UniqueConstraint(
                fields=['code'],
                condition=models.Q(language=None),
                name='unique_code_when_language_null'
            )
        ]
    #In case of language is null, code should be unique across all languages
    #In one language, code should be unique
    def __str__(self):
        return self.name
    

class Word(models.Model):
    lemma = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    part_of_speech = models.ForeignKey(PartOfSpeech, on_delete=models.SET_NULL, null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('lemma', 'language')
    def __str__(self):
        return self.lemma
    
class WordMeaning(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='meanings')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    short_definition = models.CharField(max_length=255)
    full_definition = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    #One word can only have one meaning in a given language,
    #Express the other meaning in full definition if needed, and use short definition for the main meaning in that language.
    #食べる
    #short_definition = "ăn"
    #full_definition  = "1. ăn 2. kiếm sống 3. ăn mòn"
    class Meta:
        unique_together = ('word', 'language')
        
    def __str__(self):
        return f'Meaning of {self.word.lemma} in {self.language.name if self.language else "unknown language"}'
    
class WordPronunciation(models.Model):
    PRONUNCIATION_TYPE_CHOICES = [
        ('ipa', 'International Phonetic Alphabet'),
        ('furigana', 'Furigana (hiragana/katakana)'),
        ("romaji",   "Romaji"),
        ("other",    "Other"),
    ]
    
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='pronunciations')
    type = models.CharField(max_length=50, choices=PRONUNCIATION_TYPE_CHOICES)  # e.g., IPA, phonetic, audio file path, etc.
    pronunciation = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('word', 'type')
        indexes = [
            models.Index(fields=['word', 'type']),
        ]
    #For a given word, there should be only one pronunciation of each type (e.g., one IPA, one furigana, etc.)
    #indexes on word and type for faster lookups when retrieving pronunciations for a word
    def __str__(self):
        return f'Pronunciation of {self.word.lemma} ({self.type})'
    
    def clean(self):
        if self.type == 'furigana':
            lang = self.word.language
            if not lang or lang.code != 'ja':
                raise ValidationError('Furigana pronunciation can only be used for words in Japanese.')
        
class WordImage(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='word_images')
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='word_images')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.word.lemma}'
    
class Kanji(models.Model):
    character = models.CharField(max_length=10, unique=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    onyomi = models.CharField(max_length=255, blank=True)
    kunyomi = models.CharField(max_length=255, blank=True)
    stroke_count = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.character
    
class KanjiMeaning(models.Model):
    kanji = models.ForeignKey(Kanji, on_delete=models.CASCADE, related_name='meanings')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    meaning = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('kanji', 'language')
        
    def __str__(self):
        return f'Meaning of {self.kanji.character} in {self.language.name if self.language else "unknown language"}'
    
class KanjiWord(models.Model):
    kanji = models.ForeignKey(Kanji, on_delete=models.CASCADE, related_name='kanji_words')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='kanji_words')
    position = models.PositiveIntegerField()  # Position of the kanji in the word (starting from 1)
    reading_in_word = models.CharField(max_length=255, blank=True)  # The reading of the kanji when used in this word
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['word', 'position'], name='unique_word_position')
        ]
        
    def save(self, *args, **kwargs):
        #auto assign if there is no position
        if self.position is None:
            max_position = KanjiWord.objects.filter(
                word=self.word
            ).aggregate(max_pos=Max('position'))['max_pos']

            self.position = (max_position or 0) + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.kanji.character} in {self.word.lemma}'
    
class Example(models.Model):
    word = models.ForeignKey(Word, on_delete=models.SET_NULL, null=True, blank=True, related_name='examples')
    kanji = models.ForeignKey(Kanji, on_delete=models.SET_NULL, null=True, blank=True, related_name='examples')
    sentence = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name='examples')    
    translation = models.TextField(blank=True)
    language_of_translation = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name='translation_examples')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.word_id and self.word:
            target = self.word.lemma
        elif self.kanji_id and self.kanji:
            target = self.kanji.character
        else:
            target = "Unknown"

        return f"{target}"
    
    def clean(self):
        if not self.word and not self.kanji:
            raise ValidationError('Example must be associated with either a word or a kanji.')