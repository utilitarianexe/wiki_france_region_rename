import pywikibot

def edit_page(new_text, page_name, edit_message):
    site = pywikibot.Site()
    page = pywikibot.Page(site, page_name)
    page.text = new_text
    page.save(edit_message)

def get_page_markup(page_name):
    site = pywikibot.Site()
    page = pywikibot.Page(site, page_name)
    text = page.text
    return text

def list_catalog():
    pass

