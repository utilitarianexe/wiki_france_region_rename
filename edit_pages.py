'''
This module is for editing the actual pages
TODO
final edit message
check for errors on regexes(might need permission)

get approval
option to use wikidata property instead of simple name replacement
(need approval for the property too)
'''

import re
import json
import time

import mwparserfromhell
from pywikibot_wrapper import edit_page, get_page_markup

from config import user_name


EDIT_PAGE_MESSAGE = ('Single page edit as testing for bot that'
                     ' is intended to handle the 2016 French region rename')

def allow_bots(text, user):
    '''
    Returns True if bots allowed to edit page false otherwise
    '''
    text = mwparserfromhell.parse(text)
    for tl in text.filter_templates():
        if tl.name in ('nobots', 'bots'):
            break
    else:
        return True
    for param in tl.params:
        bots = [x.lower().strip() for x in param.value.split(",")]
        if param.name == 'allow':
            if ''.join(bots) == 'none': return False
            for bot in bots:
                if bot in (user, 'all'):
                    return True
        elif param.name == 'deny':
            if ''.join(bots) == 'none': return True
            for bot in bots:
                if bot in (user, 'all'):
                    return False
    return False


def region_remap(region):
    '''
    Note 6 of the regions are staying the same
    '''
    #handle specific case where normal article name is not used
    if region == 'Auvergne (region)|Auvergne':
        region = 'Auvergne'

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

    if match_object is None:
        return None, 'regular expression did not find match in article'

    try:
        old_region_name = match_object.group(1)
        if old_region_name is None:
            old_region_name = match_object.group(2) # regs can match 2 options so need to check second
            span_index = 2
        else:
            span_index = 1
    except IndexError:
        return None, 'tried to get a group number higher than the number of groups in the re'

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
    if not allow_bots(article_text, user_name):
        return 'blocked for bot edits'

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

def fix_articles_of_type(list_function, regular_expression_pattern, actually_edit, sleep_time,
                         dot_all=False, max_pages_to_run_on_per_type=None):
    for i, article in enumerate(list_function()[10000:]):
        time.sleep(sleep_time)
        if i > max_pages_to_run_on_per_type:
            break
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
                print(message)
                continue
                #return message
    return None

def fix_all_articles(actually_edit, sleep_time, max_pages_to_run_on_per_type=None):
    commune_regex = r'\{\{Infobox French commune.*\|region.*= (.*)\n\|department'
    department_regex = r'subdivision_type1.*\[\[Regions of France\|Region\]\]\n\| subdivision_name1.*= \[\[(.*)\]\]'
    arrondissement_regex = r'rég=\[\[(.*)\]\]|subdivision_type1.*\[\[Regions of France\|Region\]\]\n\| subdivision_name1.*= \[\[(.*)\]\]'
    

    article_fixers = [[list_of_arrondissements_articles, arrondissement_regex, False],
                      [list_of_department_articles, department_regex, False],
                      [communes_from_chache, commune_regex, True]]

    
    for article_fixer in article_fixers:
        error = fix_articles_of_type(article_fixer[0], article_fixer[1], actually_edit,
                                     sleep_time,
                                     dot_all=article_fixer[2],
                                     max_pages_to_run_on_per_type=max_pages_to_run_on_per_type)
        if error is not None:
            print(error)
            break

def fix_commune_first_sentences(actually_edit, max_pages_to_run_on_per_type, sleep_time):
    commune_regex = r"\{\{Infobox French commune.*\}\}\n{1,2}'''.*''' is a French \[\[Communes of France\|commune\]\].*in the \[\[(.*)\]\] region.*\.\n"
    error = fix_articles_of_type(communes_from_chache, commune_regex,
                                 actually_edit,
                                 sleep_time,
                                 dot_all=True,
                                 max_pages_to_run_on_per_type=max_pages_to_run_on_per_type)
    if error is not None:
        print(error)




if __name__ == '__main__':
    # print(replace_region_in_article('Arrondissement of Gex',
    #                                 r'rég=\[\[(.*)\]\]|subdivision_type1.*\[\[Regions of France\|Region\]\]\n\| subdivision_name1.*= \[\[(.*)\]\]',
    #                                 False))
    #fix_all_articles(False, 0.5, max_pages_to_run_on_per_type=50)
    fix_commune_first_sentences(False, 1, 0.5)

