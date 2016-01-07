'''
This module is for editing the actual pages
TODO
final edit message
check for errors on regexes(might need permission)

set up account for bot
get approval
option to use wikidata property instead of simple name replacement
(need approval for the property too)
'''

import re
import json
from pywikibot_wrapper import edit_page, get_page_markup


EDIT_PAGE_MESSAGE = ('Single page edit as testing for bot that'
                     ' is intended to handle the 2016 French region rename')

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
                  "Provence-Alpes-Côte d'Azur": "Provence-Alpes-Côte d'Azur",}

    if region in old_to_new.values():
        return None, 'previously_changed'
    new_region = old_to_new.get(region, None)

    if new_region is None:
        return None, 'old region name not found for {}'.format(region)
    else:
        return new_region, None


def replace_region_in_text(article_text, regular_expression_pattern, dot_all=False):
    if not dot_all:
        match_object = re.search(regular_expression_pattern, article_text)
    else:
        match_object = re.search(regular_expression_pattern, article_text, re.DOTALL)
    old_region_name = match_object.group(1)
    if old_region_name is None:
        old_region_name = match_object.group(2) # regs can match 2 options so need to check second
        span_index = 2
    else:
        span_index = 1

    if old_region_name is None:
        return None, 'could not match to first or second group'
    new_region_name, error = region_remap(old_region_name)
    if error is not  None:
        return None, error
    start_index, end_index = match_object.span(span_index)
    new_text = '{start_text}{new_text}{end_text}'.format(start_text=article_text[:start_index],
                                                         new_text=new_region_name,
                                                         end_text=article_text[end_index:])
    return new_text, None


def replace_region_in_article(article_name, regular_expression_pattern, actually_edit,
                              dot_all=False):
    article_text = get_page_markup(article_name)
    new_text, error = replace_region_in_text(article_text, regular_expression_pattern,
                                             dot_all=dot_all)
    if error is not None:
        return error

    if actually_edit:
        edit_page(new_text, article_name, EDIT_PAGE_MESSAGE)

    return None

def list_of_department_articles():
    '''
    need to get the list of all 300+ of these things
    not to mention all the other ones we will need

    currently pulls them out of the markup of the list article on wikipedia
    saved as a local file(we only plan on doing this once

    Tried various other ways of getting a list
    but I think this is going to be our best effort go at this
    '''
    article_titles = []
    with open('list_of_departements_table_markup') as table_file:
        table_string = table_file.read()
        links = re.finditer(r'\[\[File:.*\n.*\[\[(.*)\|.*\]\]|\[\[File:.*\n.*\[\[(.*)\]\]',
                            table_string)
        for link in links:
            if link.group(1) is not None:
                article_titles.append(link.group(1))
            else:
                article_titles.append(link.group(2))
    return article_titles

def list_of_arrondissements_articles():
    article_titles = []
    with open('list_of_arrondissements_table_markup') as table_file:
        table_string = table_file.read()
        links = re.findall(r'\[\[Arrondissement.*\]\]', table_string)
        for link in links:
            article_title = link[2:link.index('|')]
            article_titles.append(article_title)
    return article_titles

def list_of_lists_of_communes():
    article_titles = []
    with open('list_of_lists_of_communes') as table_file:
        table_string = table_file.read()
        links = re.finditer(r'\[\[(Communes.*)\]\]', table_string)
        for link in links:
            article_titles.append(link.group(1))

    return article_titles

def communes_from_list_of_communes_markup(markup):
    article_titles = []
    links = re.finditer(r'\| \[\[(.*)\|.*\]\]|\| \[\[(.*)\]\]', markup)
    for link in links:
        if link.group(1) is not None:
            article_titles.append(link.group(1))
        else:
            article_titles.append(link.group(2))

    return article_titles

def communes_from_list_of_communes(article_name):
    print('getting: ' + article_name)
    markup = get_page_markup(article_name)
    return communes_from_list_of_communes_markup(markup)

def list_of_communes_articles():
    communes = []
    meta_commune_list = list_of_lists_of_communes()
    for commune_list in meta_commune_list:
        communes = communes + communes_from_list_of_communes(commune_list)

    return communes

def cache_communes(communes):
    json.dump(communes, open('commune_cache', 'w'))

def communes_from_chache():
    return json.load(open('commune_cache'))

def fix_articles_of_type(list_function, regular_expression_pattern, actually_edit,
                         dot_all=False):
    for article in list_function():
        print('attempting to edit {}'.format(article))
        error = replace_region_in_article(article, regular_expression_pattern, actually_edit,
                                          dot_all=dot_all)
        if error is not None:
            if error == 'previously_changed':
                message = '{} already has a new region it is being skipped'
                message = message.format(article)
                print(message)
                continue
            else:
                message = 'some kind of fatal error handling: {} : stopping all editing: {}'
                message = message.format(article, error)
                return message
    return None

def fix_all_articles(actually_edit):
    commune_regex = r'\{\{Infobox French commune.*\|region.*= (.*)\n\|department'
    department_regex = r'subdivision_type1.*\[\[Regions of France\|Region\]\]\n\| subdivision_name1.*= \[\[(.*)\]\]'
    arrondissement_regex = r'rég=\[\[(.*)\]\]|subdivision_type1.*\[\[Regions of France\|Region\]\]\n\| subdivision_name1.*= \[\[(.*)\]\]'
    

    article_fixers = [[list_of_arrondissements_articles, arrondissement_regex, False],
                      [list_of_department_articles, department_regex, False],
                      [communes_from_chache, commune_regex, True]]
    for article_fixer in article_fixers:
        error = fix_articles_of_type(article_fixer[0], article_fixer[1], actually_edit,
                                     dot_all=article_fixer[2])
        if error is not None:
            print(error)
            break

if __name__ == '__main__':
    actually_edit = False #if false will just check regular expressions not edit page
    fix_all_articles(actually_edit)
