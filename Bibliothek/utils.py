from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Zotero_Buch, Autor
from pyzotero import zotero
from datetime import date
import re


def Zotero_to_DB():
    zot = zotero.Zotero(settings.ZOTERO_USER_ID, settings.ZOTERO_LIBRARY_TYPE, settings.ZOTERO_API_KEY)
    zot2 = zotero.Zotero(settings.ZOTERO_USER_ID, settings.ZOTERO_LIBRARY_TYPE, settings.ZOTERO_API_KEY)
    parameters = {
        'itemType': 'book',
        'limit': 100,
        # 'q': 'Taghizadegan'
    }
    books = zot.items(**parameters)
    re_year = re.compile(r'[0-9]{4}')

    count = 0
    while True:
        if count >= 5:
            break
        count += 1

        for book in books:
            try:
                local_book = Zotero_Buch.objects.get(slug=book['data']['key'])
                local_book.bezeichnung = book['data']['title']
            except ObjectDoesNotExist:
                local_book = Zotero_Buch(slug=book['data']['key'],
                                         bezeichnung=book['data']['title'])
            if 'date' in book['data']:
                year = re_year.match(book['data']['date'])
                if year:
                    local_book.jahr = date(year=int(year.group()), month=1, day=1)
            if 'language' in book['data']:
                local_book.sprache = book['data']['language']

            if book['meta']['numChildren']:
                children = zot2.children(book['data']['key'])
                for child in children:
                    if child['data']['itemType'] == 'attachment' and 'filename' in child['data']:
                        format = child['data']['filename'].split('.')[-1]
                        if format in local_book.arten_liste:
                            setattr(local_book, format, child['data']['key'])
                            setattr(local_book, 'ob_%s' % format, True)

            local_book.save()
            print(local_book.bezeichnung, 'saved.')

            for creator in book['data']['creators']:
                try:
                    local_creator = Autor.objects.get(vorname=creator['firstName'], nachname=creator['lastName'])
                except ObjectDoesNotExist:
                    local_creator = Autor(vorname=creator['firstName'], nachname=creator['lastName'])
                    local_creator.save()
                except KeyError:
                    local_creator = Autor.objects.get(nachname=creator['name'])
                local_book.autoren.add(local_creator)

        try:
            zot.follow()
        except StopIteration:
            break
