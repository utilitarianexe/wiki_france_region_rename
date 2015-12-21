'''
This module is for editing the actual pages

chack usser talk page for updates
decide how many places to edit
read about wikidata
'''

from pywikibot_wrapper import edit_page, get_page_markup

def replace_region_in_text(text):
    # try:
    #     info_box_start = text.find('{{Infobox department')
    # except: #TODO better exception
    #     return None, 'can not find department info box this a fatal error'

    return text

def edit_markup_arrondissement(article_name):
    '''
    So the idea is going to be being conservative at first doing a pure info box edit
    '''
    article_text = get_page_markup(article_name)
    new_text = replace_region_in_text(article_text)
    print(new_text)


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

if __name__ == '__main__':
    edit_markup_arrondissement('Arrondissement of Belley')
