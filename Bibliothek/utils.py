from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Zotero_Buch, Autor, Kollektion
from pyzotero import zotero
from datetime import date
import re
from pprint import pprint


def collections(collections):
    '''Returns an ordered dictionary of all collections'''

    def getdict(parent_key, items):
        '''Sorts parent and childcollections in a dictionary'''
        child_parents = [item['data']['parentCollection'] for item in items]
        if parent_key in child_parents:
            # Wenn Kind vorhanden, gib dict aller Kinder zurück
            return {child['data']['key']: (child, getdict(child['data']['key'], items))
                    for child in items if child['data']['parentCollection'] == parent_key}
        else:
            return None

    return getdict(False, collections)  # 'False' is original parent


def get_collections():
    zot = zotero.Zotero(settings.ZOTERO_USER_ID, settings.ZOTERO_LIBRARY_TYPE, settings.ZOTERO_API_KEY)
    collections = zot.collections()

    def save_collections(parent_key, items):
        '''Sorts parent and childcollections in a dictionary'''
        children = [item for item in items if item['data']['parentCollection'] == parent_key]
        for child in children:
            local_collection, created = Kollektion.objects.get_or_create(slug=child['data']['key'],
                                                                         defaults={'bezeichnung': child['data']['name']})
            if parent_key:
                local_collection.parent = Kollektion.objects.get(slug=child['data']['parentCollection'])
                local_collection.save()
            save_collections(child['data']['key'], items)
            print(child['data']['name'], 'saved.')

    save_collections(False, collections)


def get_collection(key):
    zot = zotero.Zotero(settings.ZOTERO_USER_ID, settings.ZOTERO_LIBRARY_TYPE, settings.ZOTERO_API_KEY)
    # books = zot.everything(zot.collection_items('HJ4PBWFR'))
    books = zot.collection_items(key)
    re_year = re.compile(r'[0-9]{4}')
    arten_liste = Zotero_Buch.arten_liste

    parents, children = [], []
    for book in books:
        if 'parentItem' in book['data']:
            children.append(book)
        else:
            parents.append(book)

    for book in parents:
        local_book, created = Zotero_Buch.objects.get_or_create(slug=book['data']['key'],
                                                                defaults={'bezeichnung': book['data']['title']})
        if 'date' in book['data']:
            year = re_year.match(book['data']['date'])
            if year:
                local_book.jahr = date(year=int(year.group()), month=1, day=1)

        if 'language' in book['data']:
            language = book['data']['language']
            # local_book.sprache = langs[language] if language in langs else language
            local_book.language = language

        # Reset all children in case they where removed
        for format in arten_liste:
            setattr(local_book, format, None)
            setattr(local_book, 'ob_%s' % format, False)

        local_book.save()

        if created:
            print(local_book.bezeichnung, 'created.')
        else:
            print(local_book.bezeichnung, 'updated.')

        for creator in book['data']['creators']:
            try:
                local_creator, created = Autor.objects.get_or_create(vorname=creator['firstName'], nachname=creator['lastName'])
            except KeyError:
                local_creator, created = Autor.objects.get_or_create(nachname=creator['name'])
                
            if created:
                print(local_creator, 'created.')
            else:
                print(local_creator, 'updated.')
            
            local_book.autoren.add(local_creator)

    for child in children:
        local_book = Zotero_Buch.objects.get(slug=book['data']['key'])
        if child['data']['itemType'] == 'attachment' and 'filename' in child['data']:
            format = child['data']['filename'].split('.')[-1]
            if format in arten_liste:
                setattr(local_book, format, child['data']['key'])
                setattr(local_book, 'ob_%s' % format, True)
                print(local_book.bezeichnung, 'updated.')
