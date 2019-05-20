from django.db import models


class Surah(models.Model):
    """Surah Model with Many-to-One relationship with Ayah Model."""
    name = models.CharField(max_length=32)
    number = models.IntegerField()


class Ayah(models.Model):
    """Ayah Model with Many-to-One relationship with AyahWord and Translation Models."""
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE)
    number = models.IntegerField()
    text_madani = models.CharField(max_length=2048)
    text_simple = models.CharField(max_length=2048)
    sajdah = models.BooleanField()


class AyahWord(models.Model):
    ayah = models.ForeignKey(Ayah, on_delete=models.CASCADE)
    text_madani = models.CharField(max_length=64)
    text_simple = models.CharField(max_length=64)
    code = models.CharField(max_length=32)


class Translation(models.Model):
    LANGUAGE_CHOICES = (
        ('EN', 'English'),
    )
    TRANSLATION_CHOICES = (
        ('transliteration', 'Transliteration'),
    )
    ayah = models.ForeignKey(Ayah, on_delete=models.CASCADE)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='EN', max_length=32)
    translation_type = models.CharField(choices=TRANSLATION_CHOICES,
                                        default='transliteration', max_length=32)
    text = models.CharField(max_length=2048)
