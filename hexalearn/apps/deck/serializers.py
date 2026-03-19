from rest_framework import serializers
from .models import Deck, Card, Folder

#FOLDER

class DeckInFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'title', 'is_public', 'created_at']
        
class FolderSerializer(serializers.ModelSerializer):
    decks = DeckInFolderSerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'decks']
        
class FolderListSerializer(serializers.ModelSerializer):
    total_decks = serializers.IntegerField(source='decks.count', read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'description', 'total_decks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FolderDetailSerializer(serializers.ModelSerializer):
    decks = DeckInFolderSerializer(many=True, read_only=True)
    total_decks = serializers.IntegerField(source='decks.count', read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'description', 'total_decks', 'created_at', 'updated_at', 'decks']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FolderWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

#DECK
class CardGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'front_text', 'back_text',
                  'hint', 'front_image', 'back_image']


class DeckDetailSerializer(serializers.ModelSerializer):
    cards = CardGetSerializer(many=True, read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)
    estimated_level_name = serializers.CharField(
        source='estimated_level.name', read_only=True)
    total_cards = serializers.IntegerField(
        source='cards.count', read_only=True)

    class Meta:
        model = Deck
        fields = [
            'id', 'title', 'description',
            'source', 'source_name',
            'estimated_level', 'estimated_level_name',
            'is_public', 'total_cards',
            'created_at', 'updated_at',
            'cards',
        ]
        
# CREATE DECK AND CARDS
class CardCreateSerializer(serializers.ModelSerializer):
    front_image = serializers.URLField(
        required=False, allow_null=True, allow_blank=True)
    back_image = serializers.URLField(
        required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Card
        fields = ['front_text', 'back_text',
                  'hint', 'front_image', 'back_image']


class DeckCreateSerialzier(serializers.ModelSerializer):
    cards = CardCreateSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Deck
        fields = [
            'id', 'title', 'description',
            'source', 'estimated_level',
            'is_public', 'cards',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        cards_data = validated_data.pop('cards_input', [])
        deck = Deck.objects.create(**validated_data)
        Card.objects.bulk_create([
            Card(deck=deck, **card_data) for card_data in cards_data
        ])
        return deck

# UPDATE DECK basic info (not including cards)
class DeckUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = [
            'title', 'description', 'is_public',
        ]
        
# UPDATE EACH CARD IN DECK (FRONT_TEXT, BACK_TEXT, HINT, FRONT_IMAGE, BACK_IMAGE)
class CardUpdateSerializer(serializers.ModelSerializer):
    front_image = serializers.URLField(
        required=False, allow_null=True, allow_blank=True)
    back_image = serializers.URLField(
        required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Card
        fields = ['id', 'front_text', 'back_text',
                  'hint', 'front_image', 'back_image']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
