test_mode = True

#use_api_login = True # not sure what this was for

console_encoding = 'utf-8'
if test_mode:
    mylang = 'test'
    family = 'test'
    usernames['test']['test'] = u'Lonjers'
else:
    mylang = 'en'
    family = 'wikipedia'
    usernames[family][mylang] = u'Lonjers'

