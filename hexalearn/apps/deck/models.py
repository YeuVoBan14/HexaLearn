from datetime import date

from django.db import models
from django.contrib.auth.models import User
from apps.home.models import Level, Source, MediaFile
# Create your models here.
class Deck(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='decks', null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, related_name='decks', null=True)
    is_public = models.BooleanField(default=False)
    estimated_level = models.ForeignKey(Level, on_delete=models.SET_NULL, related_name='decks', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    front_text = models.TextField()
    back_text = models.TextField()
    hint = models.TextField(blank=True, null=True)
    
    front_image = models.ImageField(upload_to="flashcard/", blank=True, null=True)
    back_image = models.ImageField(upload_to="flashcard/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Card in {self.deck.title}"
   
# repetition = 1 → interval = 1 days
# repetition = 2 → interval = 6 days
# repetition > 2 → interval = old_interval × ease_factor 
class StudyState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_states')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='study_states')
    #amount of times the user has successfully recalled this card
    repetition = models.IntegerField(default=0)
    interval_days = models.IntegerField(default=1)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    last_result = models.BooleanField(default=False)
    next_review = models.DateField(default=date.today)
    review_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'card')

    def __str__(self):
        return f"StudyState for {self.user.username} - {self.card.front_text[:20]}"