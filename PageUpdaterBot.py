import urllib
import requests
from bs4 import BeautifulSoup

user='PageUpdaterBot'
passw='hqk-NGF-S6z-qqF'
baseurl='http://wikipast.epfl.ch/wikipast/'
summary='Wikipastbot update'

# Login request
payload={'action':'query','format':'json','utf8':'','meta':'tokens','type':'login'}
r1=requests.post(baseurl + 'api.php', data=payload)

#login confirm
login_token=r1.json()['query']['tokens']['logintoken']
payload={'action':'login','format':'json','utf8':'','lgname':user,'lgpassword':passw,'lgtoken':login_token}
r2=requests.post(baseurl + 'api.php', data=payload, cookies=r1.cookies)

#get edit token2
params3='?format=json&action=query&meta=tokens&continue='
r3=requests.get(baseurl + 'api.php' + params3, cookies=r2.cookies)
edit_token=r3.json()['query']['tokens']['csrftoken']

edit_cookie=r2.cookies.copy()
edit_cookie.update(r3.cookies)

# 1. Récupérer les dernières pages modifiées.

result=requests.post(baseurl+'api.php?action=feedrecentchanges')
for page in result:
    print(page)
    print('====================== Nouvelle page ======================')
    #TODO main loop


# soup=BeautifulSoup(result.text, "lxml")
# #soup=BeautifulSoup(result.text)
# code=''
# for primitive in soup.findAll("text"):
#     code+=primitive.string
# print(code)

# 2. changer le contenu

# for name in names:
#         content='\n'
#         content+='==Contenu rajoutté=='
#         content+=''
#         payload={'action':'edit','assert':'user','format':'json','utf8':'','appendtext':content,'summary':summary,'title':name,'token':edit_token}
#         r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)
#         print(r4.text)
