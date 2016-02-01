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
import random

import mwparserfromhell
from pywikibot_wrapper import edit_page, get_page_markup

from config import user_name


EDIT_PAGE_MESSAGE = ('Remove unused region and department parameters from [[Template:Infobox French commune]] '
                     ' to prevent confusion INSEE field is used now. See [[Wikipedia:Bots/Requests_for_approval/Lonjers_french_region_rename_bot]]')

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

def cache_edit_list(edited_articles):
    json.dump(edited_articles, open('edited_articles', 'w'))

def get_edit_list():
    return json.load(open('edited_articles'))

def communes_from_chache():
    return json.load(open('commune_cache'))

def randomize_cache():
    communes = communes_from_chache()
    random.shuffle(communes)
    print(len(communes))
    cache_communes(communes)


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
            # regs can match 2 options so need to check second
            old_region_name = match_object.group(2)
            span_index = 2
        else:
            span_index = 1
    except IndexError:
        return None, 'tried to get a group number higher than the number of groups in the re'

    print(old_region_name)
    if old_region_name is None:
        return None, 'could not match to first or second group'

    start_index, end_index = match_object.span(span_index)
    new_text = '{start_text}{new_text}{end_text}'.format(start_text=article_text[:start_index],
                                                         new_text='',
                                                         end_text=article_text[end_index:])
    return new_text, None


def replace_region_in_article(article_name, regular_expression_pattern, actually_edit,
                              dot_all=False):
    # needed because
    # One of the lists of communes is formated such that both
    # the communes and the catons of the department are picked up
    # so we neeed to skip the Canton articels
    # finally a few of the communes are only historical communes and lack the info box
    # a few others also are already edited
    # note these still get added to the article list
    articles_to_skip = ['Saint Barthélemy', 'Acoua']
    if article_name[:6] == 'Canton' or article_name in articles_to_skip:
        return None
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


def fix_articles_of_type(list_function, regular_expression_pattern, actually_edit, sleep_time,
                         dot_all=False, max_pages_to_run_on_per_type=None,
                         number_to_skip=0,
                         edited_articles=None):
    articles = list_function()
    for i, article in enumerate(articles[number_to_skip:]):
        time.sleep(sleep_time)
        if i >= max_pages_to_run_on_per_type:
            break

        if article in edited_articles:
            print('attempting to edit an article already edited aborting this should never happen')
            break

        print('attempting to edit {}'.format(article))
        error = replace_region_in_article(article, regular_expression_pattern, actually_edit,
                                          dot_all=dot_all)
        if error is None:
            edited_articles.append(article)
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
                break

    return edited_articles


def remove_region_from_commune_info_boxes(actually_edit, max_pages_to_run_on_per_type,
                                          sleep_time, number_to_skip):
    commune_regex = r'\{\{Infobox French commune.*(\|region.*=.*\n\|department\s*= [^\n]*\n)\|.*\|'
    only_department_regex = r'\{\{Infobox French commune.*(\|department\s*= [^\n]*\n)\|.*\|'
    commune_regex = commune_regex + '|' + only_department_regex
    edited_articles = get_edit_list()
    edited_articles = fix_articles_of_type(communes_from_chache, commune_regex,
                                           actually_edit,
                                           sleep_time,
                                           dot_all=True,
                                           max_pages_to_run_on_per_type=max_pages_to_run_on_per_type,
                                           number_to_skip=number_to_skip,
                                           edited_articles=edited_articles)
    cache_edit_list(edited_articles)
    


if __name__ == '__main__':
    remove_region_from_commune_info_boxes(True, 4, 0.5, 76)
    print(len(get_edit_list()))
    #randomize_cache()
    # commune_regex = r'\{\{Infobox French commune.*(\|region.*=.*\n\|department\s*= \S*\n)\|.*\|INSEE'
    # article_name = 'Ancelle'
    # print(replace_region_in_article(article_name, commune_regex, True,
    #                                 dot_all=True))

