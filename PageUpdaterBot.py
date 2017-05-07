# coding: utf-8
import urllib
import requests
import json
import re
from bs4 import BeautifulSoup

passw = 'hqk-NGF-S6z-qqF'
baseurl = 'http://wikipast.epfl.ch/wikipast/'
summary = 'Wikipastbot update'

user = 'PageUpdaterBot' #nom du bot
HUBPage = baseurl + 'index.php/PageUpdaterBot' #Page contenant les méta information de PUB, notamment son compteur d'IDs.
beginID = '&beginID&'
endID = '&endID& -->'
metaInfo = '<!-- PUB METAINFOS : ID = ' + beginID #synthaxe des métainfos présentes sur le HUB du bot

# Login request
payload = {'action':'query','format':'json','utf8':'','meta':'tokens','type':'login'}
r1 = requests.post(baseurl + 'api.php', data = payload)

#login confirm
login_token = r1.json()['query']['tokens']['logintoken']
payload = {'action':'login','format':'json','utf8':'','lgname':user,'lgpassword':passw,'lgtoken':login_token}
r2 = requests.post(baseurl + 'api.php', data = payload, cookies = r1.cookies)

#get edit token2
params3 = '?format=json&action=query&meta=tokens&continue='
r3 = requests.get(baseurl + 'api.php' + params3, cookies = r2.cookies)
edit_token = r3.json()['query']['tokens']['csrftoken']

edit_cookie = r2.cookies.copy()
edit_cookie.update(r3.cookies)



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
		pageTitle = u
		allEntries = parseEntries(contenu)

		for entry in allEntries:
			if getPUBId(entry) == None:
				PUBId = PUBId + 1
				updatePUBId(entry, PUBId)
				#Important, à partir de ce moment la getPUBId(entry) devrait plus pouvoir retourner None !

			pagesConcerned=getHyperLinks(entry, pageTitle)
			for name in pagesConcerned:
				urlFetched = getWikiPastUrl(name)
				if urlFetched == None:
					#ilavec n'y a pas d'Url qui correspond à notre hypermot, donc on doit créer cette page
					urlFetched = createNewPage(name)

				fillePageContenu = fetchPageData(urlFetched)
				fillePageEntries = parseEntries(fillePageContenu)

				#ensuite on créé un index des différentes entrées selon leur PUBId 
				#IdAndEntry est une liste de tuples de la forme (PUBId: Int, Entries : String) 
				IdAndEntry = map(lambda e: (getPUBId(e), e), fillePageEntries)
				found = False
				currPUBId = getPUBId(entry)
				#Le coeur de PUB on update les entrées selon l'entrée qu'on dispose nous.
				for t1, t2 in IdAndEntry:
					#On regarde d'abord si on a le même ID:
					if t1 != None:
						if t1 == currPUBId:
							#on a trouvé Un Id qui match, on overwrite l'entrée par celle de la page courante.
							t2 = entry
							found=True
					else:
						#On un entrée indexée par "None", donc il faut regarder si les deux entrées sont similaires pour l'updater correctement.
						if areEntrySimilar(entry, t2):
							t2 = entry
							found=True

				if not found:
					#Puisqu'aucune entrée matche, soit avec le PUBId soit avec leur similarité, on doit ajouter cette entrée comme une nouvelle entrée.
					IdAndEntry.append((currPUBId, entry))

				#A présent qu'on a updaté tout comme il fallait, on peut mettre en ligne les modifications sur la page.
				contentTuUp = unParseEntries(map(lambda t1, t2: t2), IdAndEntry)
				uploadModifications(contentTuUp, urlFetched)

	#le bot a finit ses modifications, il va à présent mettre à jour le PUBId de sa page avec le dernier PUBId attribué.
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
def fetchPUBmetaInfo():
	HUBcontent = fetchPageData(user)
	result = re.search(beginID + '(.*)' + endID, HUBcontent)
	result = result.group(1)
	if result == None: #TODO si les balises ont été modifiées
		currentID = '0'
		#write metainfo to HUB
		newMetaInfo = metaInfo + currentID + endID
		newContent = newMetaInfo + '\n'
		payload={'action':'edit','assert':'user','format':'json','utf8':'','prependtext':newContent,'summary':summary,'title':user,'token':edit_token}
		r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)
	else:
		currentID = result


	#TODO erreur ??
	return currentID

# Cette fonction doit être appelée après que 
# PUB ait fait toute sa traversée, elle doit
# actualiser l'ID contenu de méta_info.
#
# @param newId : Int 
#				Le nouvel ID a inscrire dans les metaInfo.
def updatePUBmetaInfo(newId):
	result=requests.post(baseurl+'api.php?action=query&titles='+user+'&export&exportnowrap')
	soup=BeautifulSoup(result.text,'html.parser')
	content=''
	for primitive in soup.findAll("text"):
		content+=primitive.string
	currentID = fetchPUBmetaInfo()
	content=content.replace(metaInfo + currentID + endID, metaInfo + str(newId) + endID)
	payload={'action':'edit','assert':'user','format':'json','utf8':'','text':content,'summary':summary,'title':user,'token':edit_token}
	r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)


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
	if fromScratch:
		#TODO
		return []
	else:
		protected_logins=["Frederickaplan","Maud","Vbuntinx","Testbot","IB","SourceBot","PageUpdaterBot","Orthobot","BioPathBot","ChronoBOT","Amonbaro","AntoineL","AntoniasBanderos","Arnau","Arnaudpannatier","Aureliver","Brunowicht","Burgerpop","Cedricviaccoz","Christophe","Claudioloureiro","Ghislain","Gregoire3245","Hirtg","Houssm","Icebaker","JenniCin","JiggyQ","JulienB","Kl","Kperrard","Leandro Kieliger","Marcus","Martin","MatteoGiorla","Mireille","Mj2905","Musluoglucem","Nacho","Nameless","Nawel","O'showa","PA","Qantik","QuentinB","Raphael.barman","Roblan11","Romain Fournier","Sbaaa","Snus","Sonia","Tboyer","Thierry","Titi","Vlaedr","Wanda"]
		depuis_date='2017-05-02T16:00:00Z'

		liste_pages=[]
		for user in protected_logins:
			result=requests.post(baseurl+'api.php?action=query&list=usercontribs&ucuser='+user+'&format=xml&ucend='+depuis_date)
			soup=BeautifulSoup(result.content,'lxml')
			for primitive in soup.usercontribs.findAll('item'):
				liste_pages.append(primitive['title'])

		return list(set(liste_pages))

'''
À l'aide du titre de la page donné en argument,
va récupérer les données de cette page, 
sous la forme d'une string

@param pageName : String
				le titre de la page wikipast où aller chercher les données.
'''
def fetchPageData(pageName):
	result=requests.post(baseurl+'api.php?action=query&titles='+pageName+'&export&exportnowrap')
	soup=BeautifulSoup(result.text, "lxml")
	pageData=''
	for primitive in soup.findAll("text"):
	    pageData+=primitive.string
	return pageData



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


'''
va récupérer le PUB_id
contenu dans cette entrée.
(Pour rappel, un PUB_id a comme forme :
"<!-- PUB_id=69 -->")
Si il n'y en a pas, retourne None,
sinon retourn le PUBId.(un int donc)

@param entry : String
			  l'entrée biographie.
'''
def getPUBId(entry):
	#TODO
	pass


'''
Va mettre à jour le PUBId de l'entrée
passée en argument si Un PUBId est présent,
Sinon va ajouter ce PUBId à l'entrée

@param entry : String
			  l'entrée biographie.
@param PUBId : Int
			  l'Id à mettre à jour sur cette page.
'''
def updatePUBId(entry, PUBId):
	#TODO
	pass

'''
retourne une liste d'hyperLinks contenu
dans cette entrée sous une forme de liste 
de String, mais en excluant de cette liste l'argument
toExclude.
'''
def getHyperLinks(entry, toExclude):
	#TODO
	pass


'''
Va créer une nouvelle page wikipast nommée selon 
l'argument donné. Si cette page existe déjà, va 
simplement retourner l'URL de la page. Autrement retourne
l'url de cette pas nouvelle créée.

@oaram name : String
			  Le nom de la page à créer.
'''
def createNewPage(name):
	#TODO
	pass


'''
va déterminer si deux entrées sont identiques.
Pour ce faire il faudra comparer que
les dates sont identiques, les lieux également
et surtout que la liste des hypermots entre
les deux entrées sont les mêmes (cf : getHyperLinks).
(ne surtout pas comparer les PUBId !!!!!)
Si toutes les conditions énumérées ci dessus
sont satisfaites, alors on renvoit True,
autrement Talse.

@param entry1 : String
				La première entrée à comparer
@param entry2 : String
				La seconde entrée avec laquelle on compare la première
'''
def areEntrySimilar(entry1, entry2):
	#TODO
	pass

'''
Va transformer une liste d'entrée
en un format que la page wikipédia va recevoir
(JSON à voir) et retourner donc ces entrées
formatée en un seul bloc de ????

@param entries : List(String)
				Les entrées nouvellement modifiées
'''
def unParseEntries(entries):
	#TODO
	pass

'''
Va uploader le contenu nouvellement modifié
sur la page indiqué par url

Note importante :
il faudrait peut être ajouter à "content" le reste
de la page (pas que la partie des entrées biographiques)
selon comment il faut uploader des modifications sur wikipast
(soit juste la partie qui change, soit toute la page)

@param content : ???? (à voir)
				le contenu à uploader
@param url : String
				L'url de la page ou mettre ces modifications.

'''
def uploadModifications(content, url):
	#TODO 
	pass

