from django.db import models


class Surah(models.Model):
    """Surah Model with Many-to-One relationship with Ayah Model."""
    name = models.CharField(max_length=32)
    number = models.IntegerField(default=0)

    def __str__(self):
        return "{} ({})".format(self.name, self.number)


class Ayah(models.Model):
    """Ayah Model with Many-to-One relationship with AyahWord and Translation Models."""
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE)
    number = models.IntegerField()
    text_madani = models.CharField(max_length=2048)
    text_simple = models.CharField(max_length=2048)
    sajdah = models.BooleanField()

    def __str__(self):
        return "{}:{} ({})".format(self.surah.number, self.number, self.text_simple)


class AyahWord(models.Model):
    ayah = models.ForeignKey(Ayah, on_delete=models.CASCADE)
    text_madani = models.CharField(max_length=64, null=True)
    text_simple = models.CharField(max_length=64, null=True)
    class_name = models.CharField(max_length=32, default="p1")
    code = models.CharField(max_length=32)
    char_type = models.CharField(max_length=32, default="word")
    number = models.IntegerField(default=0)

    def __str__(self):
        return "{}:{}, {} ({})".format(self.ayah.surah.number, self.ayah.number,
                                       self.number, self.text_simple)


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

    def __str__(self):
        return "{}:{}, {} ()".format(self.ayah.surah.number, self.ayah.number,
                                     self.translation_type, self.text)
