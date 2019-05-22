from django.core.management.base import BaseCommand
import json
from quran.models import Surah, Ayah, AyahWord, Translation
from tqdm import tqdm

DATA_JSON_PATH = '/home/piraka/Downloads/data-words.json'
UTH_JSON_PATH = '/home/piraka/Downloads/data-uthmani.json'


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get the surah names
        with open(UTH_JSON_PATH, encoding='utf-8') as uth_json_file:
            quran = json.load(uth_json_file)
            quran = quran['quran']
            surah_name_list = []
            for i, surah in tqdm(enumerate(quran['surahs']), desc='Surah Names'):
                surah_name_list.append(surah['name'])
                
        with open(DATA_JSON_PATH, encoding='utf-8') as data_json_file:
            data_file = json.load(data_json_file)
            # Go over each surah
            for surah, verses in tqdm(data_file.items(), desc='Surahs', total=114):
                surah_num = int(surah)
                new_surah, created = Surah.objects.get_or_create(
                        number=surah_num, name_ar=surah_name_list[surah_num-1])

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
                        class_name = word['class_name']
                        char_type = word['char_type']
                        try:
                            new_word = AyahWord.objects.get(number=i,
                                                            ayah=new_ayah,
                                                            text_simple=text_simple,
                                                            code=code,
                                                            class_name=class_name,
                                                            char_type=char_type)
                        except AyahWord.DoesNotExist:
                            new_word = AyahWord(number=i,
                                                ayah=new_ayah,
                                                text_madani=text_madani,
                                                text_simple=text_simple,
                                                code=code,
                                                class_name=class_name,
                                                char_type=char_type)
                            new_word.save()
