# coding: utf-8
import urllib
import requests
import json
from bs4 import BeautifulSoup

user='PageUpdaterBot'
passw='hqk-NGF-S6z-qqF'
baseurl='http://wikipast.epfl.ch/wikipast/'
summary='Wikipastbot update'
#Page contenant les méta information de PUB, notamment son compteur d'IDs.
HUBPage='http://wikipast.epfl.ch/'

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

result=requests.post(baseurl+'api.php?action=feedrecentchanges&export&exportnowrap')
soup=BeautifulSoup(result, "xml")
code=''
for primitive in soup.findAll("text"):
    code+=primitive.string
print(code)

main()
#test()


# Définis à part du code du main, chaque fonction
# devrait idéalement être testée, si possible ici.
# mais après on fait comme on veut.
def test():
	#TODO
	pass

#--------- main code-------------------
def main():
	# Récupération de l'Id de base pour les PUB_id
	PUBId = fetchPUBmetaInfo(HUBPage)

	# Récupération de la liste de pages à parcourir.
	pagesToMod = []
	if PUBId == 0:
		pagesToMod = getPageList(True)
	else:
		pagesToMod = getPageList(False)

	## boucle d'action principale du code.
	for u in pagesToMod:
		contenu = fetchPageData(u)
		pageTitle = getTitle(contenu)
		allEntries = parseEntries(contenu)

		for entry in allEntries:
			


	#TODO

	updatePUBmetaInfo(HUBPage, PUBId)


# Cette fonction va s'occuper d'aller sur la page
# indiquée en argument et regarder si elle trouve le bloc
# de méta information de PUB (bloc commençant par 
# "<!-- PUB METAINFOS :").
# Si ce bloc de méta info
# est présent, elle va retourner l'Id qui y 
# est contenu (représentant le dernier Id attribué
# à une entrée de page).
# Si ce bloc de méta info n'est pas présent,
# cette fonction va s'occuper de le créer,
# y mettre comme valuer d'ID 0, puis retourner
# 0. (forcément)
# Si une quelquonque erreur s'est produite,
# la fonction retournera un chiffre négatif
# ou bien enverra une exception (comme vous le sentez)
#
# @param page: String 
#			   la page ou aller chercher les métaInfo.
def fetchPUBmetaInfo(page):
	#TODO
	pass

# Cette fonction doit être appelée après que 
# PUB ait fait toute sa traversée, elle doit
# actualiser l'ID contenu de méta_info.
# Si pour une quelconque raison le bloc
# méta info n'existe pas, la fonction doit le recréer
# et l'initialiser avec le correct ID.
#
# @param page : String
#				la page ou aller chercher les métaInfo.
# @param newId : Int 
#				Le nouvel ID a inscrire dans les metaInfo.
def updatePUBmetaInfo(page, newId):
	#TODO
	pass

'''
En fonction de la variable fromScratch,
cette fonction va récupérer la liste des pages qui
ont été modifiées récemment, ou bien
toutes les pages sur lequel on veut établir
un indexage par PUBId.
Elle retournera la liste des pages sous
la forme d'une liste d'url wikipast.

@para fromScratch : Boolean
				 vaut true si on veut faire un indexage depuis 0
				 ou false si on veut juste récupérer les pages
				 récemment modifiées.
'''
def getPageList(fromScratch):
	#TODO
	pass

'''
A l'aide de l'url donné en argument,
va récupérer les données de cette page,
sous le format qui vous plaît (JSON je suppose ?)

@param pageUrl : String
				l'url de la page wikipast ou aller chercher les données.
'''
def fetchPageData(pageUrl):
	#TODO
	pass

'''
va bêtement récupérer le titre
de la page courante et le renvoyer
sous forme de String.

@param content : ???? (à voir)
				le contenu de la page
'''
def getTitle(content):
	#TODO
	pass

'''
Va s'occuper de trier le contenu
de la page donné en argument
pour en ressortir que les entrées biographies
sourcées (il faudra donc éviter si ils on rajouté
du texte autre part qui n'a rien à voir).
Une entrée est normalement écrite sous la forme (dans le code):
* [[YYYY.MM.JJ]] / [[<lieu>]]. [[<évènement>]] entre [[<Mr. X>]] et [[<Mr.Y>]]. [<référence>]

!! remarque importante que je na'vais pas pensé avant :
Où met-on le PUB_id ? (il sera de la forme "<!-- PUB_id=69-->") ?
Il faut penser qu'on doit le mettre dans un endroit stratégique,
car il faudrait que si d'autres bots reprennent ou modifient des entrées,
ils conservent l'intégrité du PUB_id.

Cette fonction retournera une liste de String qui constituent
les entrées retournées sous la forme montrée plus haut.

@param content : ???? (à voir)
				le contenu de la page
'''
def parseEntries(content):
	#TODO
	pass



## garbage, kept for historical reason.

# for name in names:
#     result=requests.post(baseurl+'api.php?action=query&titles='+name+'&export&exportnowrap')
#     soup=BeautifulSoup(result.text, "lxml")
#     #soup=BeautifulSoup(result.text)
#     code=''
#     for primitive in soup.findAll("text"):
#         code+=primitive.string
#     print(code)


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
