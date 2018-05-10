from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Zotero_Buch, Autor, Kollektion
from pyzotero import zotero
from datetime import date
import re
import sys
import time
from pprint import pprint
import logging


def collections(collections):  # TODO: noch relevant?
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
    '''
    Pullt und sichert alle Zotero Kollektionen.
    '''
    print('retrieving collections...')
    zot = zotero.Zotero(settings.ZOTERO_USER_ID, settings.ZOTERO_LIBRARY_TYPE, settings.ZOTERO_API_KEY)
    collections = zot.collections()
    
    def save_collections(parent_key, items):
        '''Sorts parent and childcollections in a dictionary'''
        children = [item for item in items if item['data']['parentCollection'] == parent_key]
        for child in children:
            local_collection, created = Kollektion.objects.get_or_create(
                slug=child['data']['key'],
                defaults={'bezeichnung': child['data']['name']})
            if parent_key:
                local_collection.parent = Kollektion.objects.get(slug=child['data']['parentCollection'])
                local_collection.save()
                save_collections(child['data']['key'], items)
                # print(child['data']['name'], 'saved.')
                
    # Check or collections to delete
    for local_collection in Kollektion.objects.all():
        if local_collection.slug not in [collection['data']['key'] for collection in collections]:
            print(local_collection.bezeichnung, 'deleted.')
            local_collection.delete()
            
    save_collections(False, collections)


def get_collection(collection):
    fails = 0
    created_books = 0
    logger = logging.getLogger(__name__)
    key = collection.slug
    print(collection.bezeichnung)

    zot = zotero.Zotero(settings.ZOTERO_USER_ID, settings.ZOTERO_LIBRARY_TYPE, settings.ZOTERO_API_KEY)
    books = zot.everything(zot.collection_items(key))
    re_year = re.compile(r'[0-9]{4}')
    arten_liste = Zotero_Buch.arten_liste

    parents, children = [], []
    for book in books:
        if 'parentItem' in book['data']:
            children.append(book)
        elif book['data'].get('itemType') == 'book':
            parents.append(book)

    for book in parents:
        try:
            title = book['data'].get('title') or book['data']['subject']  # Sometimes title is missing
            local_book, created = Zotero_Buch.objects.get_or_create(
                slug=book['data']['key'],
                defaults={'bezeichnung': title})
            if 'date' in book['data']:
                year_match = re_year.match(book['data']['date'])
                if year_match:
                    year = int(year_match.group())
                    if year:
                        local_book.jahr = date(year=year, month=1, day=1)

            if 'language' in book['data']:
                language = book['data']['language']
                # local_book.sprache = langs[language] if language in langs else language
                local_book.language = language

            # Reset all children in case they where removed
            for format in arten_liste:
                setattr(local_book, format, None)
                setattr(local_book, 'ob_%s' % format, False)

            local_book.save()
            local_book.kollektion.add(collection)
            
            if created:
                created_books += 1

            # sys.stdout.write("\r%s" % local_book.bezeichnung)
            # sys.stdout.flush()

            for creator in book['data'].get('creators', []):
                # if 'lastName' in creator:
                name = creator.get('lastName', creator.get('name'))
                if name:
                    local_creator, created = Autor.objects.get_or_create(vorname=creator.get('firstName'), nachname=name)
                # else:
                #     local_creator, created = Autor.objects.get_or_create(vorname=None, nachname=creator['name'])

                local_book.autoren.add(local_creator)
        except KeyError as e:
            logger.exception(book)
            fails += 1

    for child in children:
        try:
            if child['data']['itemType'] == 'attachment' and 'filename' in child['data']:
                format = child['data']['filename'].split('.')[-1]
                if format in arten_liste:
                    local_book = Zotero_Buch.objects.get(slug=child['data']['parentItem'])
                    setattr(local_book, format, child['data']['key'])
                    setattr(local_book, 'ob_%s' % format, True)
                    # sys.stdout.write("\r%s" % local_book.bezeichnung)
                    # sys.stdout.flush()
        except ObjectDoesNotExist as e:
            logger.error('Missing parent:', child)
            fails += 1

    print('Created: %d, Fails: %d' % (created_books, fails))
    return parents


def zotero_import():
    start = time.time()

    get_collections()
    book_list = []
    for collection in Kollektion.objects.all():
        parents = get_collection(collection)
        book_list += parents

    # Check for books to delete
    book_keys = [book['data']['key'] for book in book_list]
    for local_book in Zotero_Buch.objects.all():
        if local_book.slug not in book_keys:
            print(local_book, 'deleted.')
            local_book.delete()

    end = time.time()
    print('Import of %d books done. Time:' % len(book_list), end - start)
