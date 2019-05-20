"""
Serializers for the Quran models.
"""
from rest_framework import serializers
from quran.models import Surah, Ayah, AyahWord, Translation


class SurahSerializer(serializers.ModelSerializer):
    class Meta:
        model = Surah
        fields = '__all__'


class AyahSerializer(serializers.ModelSerializer):
    surah = SurahSerializer

    class Meta:
        model = Ayah
        fields = '__all__'


class AyahWordSerializer(serializers.ModelSerializer):
    ayah = AyahSerializer

    class Meta:
        model = AyahWord
        fields = '__all__'


class TranslationSerializer(serializers.ModelSerializer):
    ayah = AyahSerializer

    class Meta:
        model = Translation
        fields = '__all__'
