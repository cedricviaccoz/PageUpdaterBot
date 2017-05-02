###############################
#### 8. scrapping web data ####
###############################

import urllib2
from bs4 import BeautifulSoup

response=urllib2.urlopen("https://fr.wikipedia.org/wiki/Liste_des_capitales_du_monde")
page_source=response.read()
soup=BeautifulSoup(page_source,'html.parser')
capitales_and_countries=[]
for primitive in soup.findAll("table"):
    if primitive.find("th").string=='Capitale':
        for cap_and_count in primitive.findAll("td"):
            for text in cap_and_count.findAll("a"):
                if text.string != None:
                    capitales_and_countries.append(unicode(text.string))
    
for i in range(len(capitales_and_countries)):
    print(capitales_and_countries[i])
print('\n'+str(len(capitales_and_countries))+' capitales and countries listed\n')

# exercice: Scrapper des prénoms sur
# https://fr.wikipedia.org/wiki/Liste_de_pr%C3%A9noms_fran%C3%A7ais_et_de_la_francophonie

##################################
#### 9. Mediawiki bot example ####
##################################

import urllib2
import requests
from bs4 import BeautifulSoup

user='testbot'
passw='dhbot2017'
baseurl='http://wikipast.epfl.ch/wikipast/'
summary='Wikipastbot update'
names=['Madame X','Monsieur Y']

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

# 1. retrouver le contenu et l'imprimer

for name in names:
    result=requests.post(baseurl+'api.php?action=query&titles='+name+'&export&exportnowrap')
    soup=BeautifulSoup(result.text, "lxml")
    #soup=BeautifulSoup(result.text)
    code=''
    for primitive in soup.findAll("text"):
        code+=primitive.string
    print(code)

# 2. changer le contenu

for name in names:
        content='\n'
        content+='==Contenu rajoutté=='
        content+='''
\nLorem ipsum dolor sit amet , consectetur adipiscing elit . Integer at pulvinar tellus . Integer neque lectus , suscipit in lorem et , mollis suscipit neque . Sed commodo orci odio . Cras accumsan id dui ut facilisis . Curabitur vulputate ultricies turpis , eget dapibus lacus tristique non . Quisque vulputate diam nec nulla eleifend , eget sollicitudin dolor dapibus . Pellentesque tristique ultrices lobortis . Sed fringilla placerat odio vel mollis . Fusce eleifend facilisis fringilla . Mauris quam velit , aliquam nec rhoncus ac , efficitur quis leo . Pellentesque lacinia arcu mollis arcu suscipit , vel blandit magna condimentum . Morbi sed elementum nunc . Suspendisse eget quam eget erat tristique fermentum . Vestibulum urna sapien , lobortis sed hendrerit sit amet , blandit et magna . In fermentum , mi quis elementum hendrerit , lacus arcu ullamcorper lectus , a sodales justo diam sed diam .
Maecenas sit amet mi mattis , faucibus lorem eu , tempus sapien . Morbi aliquam commodo ligula nec tincidunt . Integer imperdiet dolor ut enim venenatis , congue gravida sem placerat . Phasellus tempus ipsum eu nisl consequat , et lacinia augue tristique . Integer diam arcu , viverra eleifend leo non , vehicula pretium risus . Donec molestie maximus quam vitae mollis . Nulla congue lacus in augue rutrum scelerisque . Phasellus facilisis neque ultricies nisl bibendum imperdiet . Duis dapibus mauris quis faucibus viverra .
Pellentesque faucibus egestas blandit . Fusce malesuada magna ut sollicitudin mollis . Fusce ut tempus felis . Aliquam eget tempus risus . Nunc et semper tellus . Curabitur imperdiet magna congue est vestibulum , eget tristique justo lacinia . Proin sodales enim dolor , sit amet viverra nibh pellentesque a . Nulla pellentesque sed purus quis viverra . Class aptent taciti sociosqu ad litora torquent per conubia nostra , per inceptos himenaeos . Nam condimentum in leo at molestie . Mauris ullamcorper maximus convallis . Ut cursus consectetur dui , vel pharetra ante ornare eget . Class aptent taciti sociosqu ad litora torquent per conubia nostra , per inceptos himenaeos . Donec dignissim ut magna non scelerisque .
Sed facilisis nulla eget est rhoncus tincidunt . Praesent eu metus non magna ullamcorper tincidunt . Morbi dui velit , aliquet non bibendum sollicitudin , tempus eu purus . Nulla dolor tortor , feugiat ac convallis vitae , rhoncus ultricies tortor . Maecenas bibendum in augue quis aliquet . Fusce at sapien dictum sem luctus malesuada . Cras posuere odio at pellentesque vehicula . Donec consequat neque non dolor varius pulvinar . Integer sit amet porttitor massa . In hac habitasse platea dictumst .
Vivamus pellentesque blandit tellus , eget hendrerit nibh varius ac . Mauris eget cursus justo . Integer at quam sit amet enim tincidunt condimentum . Donec egestas lacinia nisi , ullamcorper imperdiet mauris rutrum eget . Donec viverra luctus efficitur . Suspendisse sed ipsum erat . Sed tincidunt urna interdum arcu sagittis volutpat . Morbi vitae dignissim massa . Ut erat sapien , vulputate vitae nisi vitae , aliquet ullamcorper nunc . Etiam volutpat mi sapien , in pellentesque massa fringilla a . Nunc sed nunc gravida , hendrerit turpis eget , molestie tortor . Vestibulum consectetur nulla at ultricies consectetur . Nam et mattis augue . Pellentesque sed dolor vel ante ultricies tristique a a felis . Etiam a nulla at arcu sodales lacinia in vel elit .\n'''
        payload={'action':'edit','assert':'user','format':'json','utf8':'','appendtext':content,'summary':summary,'title':name,'token':edit_token}
        r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)
        print(r4.text)

# exercice: Faire un bot qui modifie le contenu de la page "Madame X" et "Monsieur Y" en fonction
# du contenu précédent. Exemple renmplacer les fautes de type "blabla . Blabla" par "blabla. Blabla".
# Astuce: utiliser la fonction "replace"
