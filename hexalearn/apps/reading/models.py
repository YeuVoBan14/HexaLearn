from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField
import re

from apps.home.models import Source, Level, Language
# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True)
    color = ColorField(default="#FFFFFF")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()
        if Topic.objects.exclude(pk=self.pk).filter(code=self.code).exists():
            raise ValueError(f"Topic with code '{self.code}' already exists.")
        super().save(*args, **kwargs)
    
    def _generate_code(self):
        code = self.name.lower()
        code = re.sub(r'[^\w\s-]', '', code)
        code = re.sub(r'\s+', '-', code.strip())
        return code
    
class Passage(models.Model):
    
    title = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover_image = models.ImageField(upload_to="reading/passage_cover", null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)
    estimated_read_time = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.cover_image:
            return self.cover_image.url
        return None
    
class Paragraph(models.Model):
    
    passage = models.ForeignKey(Passage, on_delete=models.CASCADE, related_name="paragraphs")
    index = models.PositiveIntegerField(default=0, blank=True)
    image = models.ImageField(upload_to="reading/paragraph/", null=True, blank=True)
    content = models.TextField()
    note = models.TextField(null=True, blank=True)
    vocabulary = models.ManyToManyField(
        'dict.Word',
        blank=True,
        related_name='paragraphs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('passage', 'index')
        
    def __str__(self):
        return f"Paragraph:#{self.index} of passage:{self.passage.title}"
    
    def save(self, *args, **kwargs):
        if not self.pk and self.index == 0:
            last = Paragraph.objects.filter(passage=self.passage).aggregate(
                max_index=models.Max('index')
            )['max_index']
            self.index = (last or 0) + 1
        super().save(*args, **kwargs)
        
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None
        
class ParagraphTranslation(models.Model):
    
    paragraph = models.ForeignKey(Paragraph, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    translation = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('paragraph', 'language')
        
    def __str__(self):
        return f"Translation for paragraph#{self.paragraph.index} of passage:{self.paragraph.passage.title}"
    
class ReadingNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reading_notes")
    paragraph = models.ForeignKey(Paragraph, on_delete=models.CASCADE, related_name="user_notes")
    selected_text = models.TextField()
    note = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Note of {self.user.username} on #{self.paragraph.index}|{self.paragraph.passage.title}"
    
class UserReadingProgress(models.Model):
    READING_PROCESSES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
    ]
    
    passage = models.ForeignKey(Passage, on_delete=models.CASCADE, related_name="user_reading_progresses")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reading_progresses")
    status = models.CharField(max_length=20, choices=READING_PROCESSES, default='started')
    percentage_read = models.PositiveIntegerField(default=0)
    last_paragraph_index = models.PositiveIntegerField(default=1)
    last_read_at = models.DateTimeField(auto_now=True)
    complete_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'passage')
    
    def __str__(self):
        return f"Reading progress of {self.user.username} on {self.passage.title} at {self.percentage_read}%"
    
    def save(self, *args, **kwargs):
        self.percentage_read = self._get_percentage_read()
        super().save(*args, **kwargs)    
    
    def _get_percentage_read(self):
        total = Paragraph.objects.filter(passage=self.passage).count()
        if total == 0:
            return 0
        return round((self.last_paragraph_index / total) * 100)