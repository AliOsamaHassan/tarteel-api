import pdb
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
                # if created:
                #     print("Created surah {}".format(surah))

                # Now go over all the ayahs
                for verse in tqdm(verses['verses'], desc='Ayahs'):
                    ayah_created = False
                    # Extract
                    sajdah = True if verse['sajdah'] else False
                    text_madani = verse['text_madani']
                    text_simple = verse['text_simple']
                    ayah_number = verse['verse_number']
                    # Check
                    if text_madani is None or text_simple is None:
                        print("NULL AYAH: {}:{}".format(surah, ayah_number))

                    # Create the ayah
                    try:
                        new_ayah = Ayah.objects.get(surah=new_surah, number=ayah_number)
                    except Ayah.DoesNotExist:
                        new_ayah = Ayah(surah=new_surah,
                                        number=ayah_number,
                                        text_madani=verse['text_madani'],
                                        text_simple=verse['text_simple'],
                                        sajdah=sajdah)
                        ayah_created = True
                        new_ayah.save()
                    # pdb.set_trace()
                    # if ayah_created:
                    #     print("Created ayah {}:{}".format(surah, ayah_number))

                    # Go over translations
                    for translation in verse['translations']:
                        translation_created = False
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
                            translation_created = True
                            new_translation.save()
                        # pdb.set_trace()
                        # if translation_created:
                        #     print("Created translation {}:{}".format(surah,
                        #                                              verse['verse_number']))

                    # Go over words
                    for word in verse['words']:
                        text_madani = word['text_madani']
                        text_simple = word['text_simple']
                        code = word['code']
                        if text_madani is None or text_simple is None:
                            continue
                        try:
                            new_word = AyahWord.objects.get(ayah=new_ayah,
                                                            text_simple=text_simple,
                                                            code=code)
                        except AyahWord.DoesNotExist:
                            new_word = AyahWord(ayah=new_ayah,
                                                text_madani=text_madani,
                                                text_simple=text_simple,
                                                code=code)
                            new_word.save()
