from django.core.management.base import BaseCommand
import json
from quran.models import Surah, Ayah, AyahWord, Translation
from tqdm import tqdm

DATA_JSON_PATH = '/home/piraka/Downloads/data-words.json'


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(DATA_JSON_PATH, encoding='utf-8') as data_json_file:
            data_file = json.load(data_json_file)
            # Go over each surah
            for surah, verses in tqdm(data_file.items(), desc='Surahs', total=114):
                new_surah, created = Surah.objects.get_or_create(number=int(surah))

                # Now go over all the ayahs
                for verse in tqdm(verses['verses'], desc='Ayahs'):
                    # Extract
                    sajdah = True if verse['sajdah'] else False
                    text_madani = verse['text_madani']
                    text_simple = verse['text_simple']
                    ayah_number = verse['verse_number']

                    # Create the ayah
                    try:
                        new_ayah = Ayah.objects.get(surah=new_surah, number=ayah_number)
                    except Ayah.DoesNotExist:
                        new_ayah = Ayah(surah=new_surah,
                                        number=ayah_number,
                                        text_madani=text_madani,
                                        text_simple=text_simple,
                                        sajdah=sajdah)
                        new_ayah.save()

                    # Go over translations
                    for translation in verse['translations']:
                        text = translation['text']
                        if translation['language_name'] != 'english':
                            print("non-english translation at: {},{}".format(
                                    surah, verse['verse_number']))

                        try:
                            new_translation = Translation.objects.get(ayah=new_ayah,
                                                                      text=text)
                        except Translation.DoesNotExist:
                            new_translation = Translation(
                                    ayah=new_ayah,
                                    text=text)
                            new_translation.save()

                    # Go over words
                    for i, word in enumerate(verse['words'], 1):
                        text_madani = word['text_madani']
                        text_simple = word['text_simple']
                        code = word['code']
                        if text_madani is None or text_simple is None:
                            continue
                        try:
                            new_word = AyahWord.objects.get(number=i,
                                                            ayah=new_ayah,
                                                            text_simple=text_simple,
                                                            code=code)
                        except AyahWord.DoesNotExist:
                            new_word = AyahWord(number=i,
                                                ayah=new_ayah,
                                                text_madani=text_madani,
                                                text_simple=text_simple,
                                                code=code)
                            new_word.save()
