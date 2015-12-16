import pywikibot

def get_page():
    site = pywikibot.Site()
    page = pywikibot.Page(site, u"User:Lonjers")
    text = page.text
    print(text)

def test():
    print('hi')

if __name__ == '__main__':
    get_page()
