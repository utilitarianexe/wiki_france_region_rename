'''
This module is for editing the actual pages

chack usser talk page for updates
decide how many places to edit
read about wikidata
'''

import re
from pywikibot_wrapper import edit_page, get_page_markup


def region_remap(region):
    '''
    Note 6 of the regions are staying the same
    '''
    old_to_new = {'Burgundy': 'Bourgogne-Franche-Comté',
                  'Franche-Comté': 'Bourgogne-Franche-Comté',
                  'Aquitaine': 'Aquitaine-Limousin-Poitou-Charentes',
                  'Limousin': 'Aquitaine-Limousin-Poitou-Charentes',
                  'Poitou-Charentes': 'Aquitaine-Limousin-Poitou-Charentes',
                  'Lower Normandy': 'Normandy',
                  'Upper Normandy': 'Normandy',
                  'Alsace': 'Alsace-Champagne-Ardenne-Lorraine',
                  'Champagne-Ardenne': 'Alsace-Champagne-Ardenne-Lorraine',
                  'Lorraine': 'Alsace-Champagne-Ardenne-Lorraine',
                  'Languedoc-Roussillon': 'Languedoc-Roussillon-Midi-Pyrénées',
                  'Midi-Pyrénées': 'Languedoc-Roussillon-Midi-Pyrénées',
                  'Nord-Pas-de-Calais': 'Nord-Pas-de-Calais-Picardie',
                  'Picardy': 'Nord-Pas-de-Calais-Picardie',
                  'Auvergne': 'Auvergne-Rhône-Alpes',
                  'Rhône-Alpes': 'Auvergne-Rhône-Alpes',
                  'Brittany': 'Brittany',
                  'Centre-Val de Loire': 'Centre-Val de Loire',
                  'Corsica': 'Corsica',
                  'Île-de-France': 'Île-de-France',
                  'Pays de la Loire': 'Pays de la Loire',
                  "Provence-Alpes-Côte d'Azur": "Provence-Alpes-Côte d'Azur",
              }
    return old_to_new.get(region, None)


def fix_region_text(old_text):
    region_name = old_text[6:-2]
    new_region = region_remap(region_name)
    if new_region is None:
        return None, 'failed to find region'
    new_text = old_text[:6] + new_region + ']]' #TODO format
    return new_text, None

def replace_region_in_text(text):
    pattern = r'rég=\[\[.*\]\]'
    match = re.search(pattern, text)
    if match is None:
        return None, 'could not find location to fix'
    text_to_fix = match.group(0) #TODO what if for than one match
    fixed_text, error = fix_region_text(text_to_fix)
    if error is not None:
        return None, error
    start_index, end_index = match.span()
    new_text = '{start_text}{new_text}{end_text}'.format(start_text=text[:start_index],
                                                         new_text=fixed_text,
                                                         end_text=text[end_index:])
    return new_text, None

def edit_markup_arrondissement(article_name):
    '''
    So the idea is going to be being conservative at first doing a pure info box edit
    '''
    article_text = get_page_markup(article_name)
    new_text, error = replace_region_in_text(article_text)
    if error is not None:
        print(error)
        return
    
    print(new_text)
    edit_page(new_text, article_name, 'testing bot')



if __name__ == '__main__':
    # woo finally go one to work on the test wiki
    article_name = 'Arrondissement of Bourg-en-Bresse'
    edit_markup_arrondissement(article_name)
