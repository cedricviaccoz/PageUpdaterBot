# coding: utf-8
import urllib
import requests
import sys
import json
import re
import hashlib
from bs4 import BeautifulSoup

passw = 'hqk-NGF-S6z-qqF'
baseurl = 'http://wikipast.epfl.ch/wikipast/'
summary = 'Wikipastbot update'

user = 'PageUpdaterBot' #nom du bot
HUBPage = baseurl + 'index.php/PageUpdaterBot' #Page contenant les méta information de PUB, notamment son compteur d'IDs.
beginID = '&beginID&'
endID = '&endID&'
titleID='entryID = '

titleHASH=' entryHash = '
beginHash = '&beginHASH&'
endHash = '&endHASH&'
metaInfo = '<!-- PUB METAINFOS : ID = ' #synthaxe des métainfos présentes sur le HUB du bot
entryMetaInfo = '<!-- PUB METAINFOS : ' #synthaxe des métainfos présentes sur les **entrées des pages**
endEntryMetaInfo=' -->' #synthaxe de fin des métainfos présentes sur les **entrées des pages**

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

# module to clean all comments left by PageUpdaterBot
def cleaner():
	pagesToMod = getPageList()
	for p in pagesToMod:
		contenu = fetchPageData(p)
		list_to_delete = re.findall(r'<!--(.*?)-->', contenu)
		newContent = contenu
		for l in list_to_delete:
			newContent = newContent.replace('<!--' + l + '-->', '')
		uploadModifications(contenu, newContent, p)
		print('Successfully cleaned current page : ' + p)


def main():
	# Récupération de l'Id de base pour les PUB_id
	PUBId = fetchPUBmetaInfo(False)

	# Récupération de la liste de pages à parcourir.
	pagesToMod = getPageList()
	listOfPagesToCompare = getPageList()

	## boucle d'action principale du code.
	for u in pagesToMod:
		contenu = fetchPageData(u)
		pageTitle = u
		allEntries = parseEntries(contenu)
		previousContent = unParseEntries(allEntries)

		originalEntries=[]

		for entry in allEntries:
			isNewEntry = False
			if getPUBId(entry) == None:
				#si l'entrée n'a pas d'ID, on lui met l'id suivant et un hash
				PUBIdInt = int(PUBId) + 1
				PUBId = str(PUBIdInt)
				PUBHASH = generateHash(entry)
				entry = setPUBInfos(entry, PUBId, PUBHASH)
				isNewEntry = True
				#Important, à partir de ce moment la getPUBId(entry) devrait plus pouvoir retourner None !
			entryToDelete = False
			originalEntryToAppend = entry
			pagesConcerned=getHyperLinks(entry, pageTitle)

			for name in pagesConcerned:
				if re.search(r'\d\d\d\d', name) == None:
					#le nom des pages dans l'url doit pas contenir d'espace.

					if isNewPage(name, listOfPagesToCompare):
						createNewPage(name)
						listOfPagesToCompare.append(name)

					name=name.replace(" ", "_")

					fillePageContenu = fetchPageData(name)
					fillePageEntries = parseEntries(fillePageContenu)

					previousFilleContent = unParseEntries(fillePageEntries)

					emptyFillePage = (previousFilleContent == None)

					#ensuite on créé un index des différentes entrées selon leur PUBId
					IdAndEntry = []
					for e in fillePageEntries:
						IdAndEntry.append((getPUBId(e), e))

					#liste qui contiendra les nouvelles entrées modifiées (ou pas) de la page fille. 
					newEntries = []
					found = False
					currPUBId = getPUBId(entry)
					#Le coeur de PUB on update les entrées selon l'entrée dont on dispose.
					for t1, t2 in IdAndEntry:
						#On regarde d'abord si on a le même ID:
						if t1 != None:
							if t1 == currPUBId:
								entryActualHash = generateHash(entry)
								if entryActualHash == getPUBHash(entry): #entry pas modifiée
									t2ActualHash = generateHash(t2)
									if t2ActualHash != getPUBHash(entry): #t2 modifiée
										originalEntryToAppend = t2 #modification dans la page mère
										newT2 = setPUBInfos(t2,t1,t2ActualHash)
										newEntries.append(newT2)
									else:
										#if entryActualHash == t2ActualHash:
										#aucune modification mais quand meme append pour pas perdre l'entrée
										newEntries.append(t2)
										#originalEntryToAppend = newT2
										

								else:
									#on overwrite l'entrée dans la page fille
									originalEntryToAppend = entry
									newT2 = setPUBInfos(entry,t1,entryActualHash)
									#et on met à jour le hash dans la page mère
									newEntries.append(newT2)
								found=True
							else:
								newEntries.append(t2)
						else:
							#On un entrée indexée par "None", donc il faut regarder si les deux entrées sont similaires pour l'updater correctement.
							if isNewEntry and areEntrySimilar(entry, t2) :

								newT2 = entry
								newEntries.append(newT2)
								found=True
							else:
								newEntries.append(t2)

					if not found:
						if isNewEntry or emptyFillePage:
							#Puisqu'aucune entrée matche, soit avec le PUBId soit avec leur similarité, on doit ajouter cette entrée comme une nouvelle entrée.
							newEntries.append(entry)
						else:
							#Supprimer l'entrée de la page mère
							entryToDelete = True


					sortedEntries = sorted(newEntries)

					#A présent qu'on a updaté tout comme il fallait, on peut mettre en ligne les modifications sur la page.
					contentToUp = unParseEntries(sortedEntries)
					if contentToUp != None:
						uploadModifications(previousFilleContent, contentToUp, name)
						print("Successfully updated dependant page : " + name)
			if not entryToDelete:
				originalEntryToAppend = setPUBInfos(originalEntryToAppend,getPUBId(originalEntryToAppend),generateHash(originalEntryToAppend))
				originalEntries.append(originalEntryToAppend)

		#On doit mettre à jour potentiellement la page originelle si on a du ajouter un PUB_Id
		uploadModifications(previousContent, unParseEntries(sorted(originalEntries)), pageTitle)
		print("Successfully updated current page : " + pageTitle)

	#le bot a finit ses modifications, il va à présent mettre à jour le PUBId de sa page avec le dernier PUBId attribué.

	updatePUBmetaInfo(int(PUBId))



'''
Récupère le PUB_id
dans le contenu passé en argument.
(Un PUB_id a la forme suivante :
"<!-- PUB_id = &beginID&69&endID& -->")
S'il n'y en a pas, retourne None,
sinon retourne le PUBId (en string).
S'il y en a plusieurs, il retourne le dernier.

@param content : String
			  le contenu dans lequel trouver l'id.
'''
def getPUBId(content):
	PUB_ID = re.search(beginID + '(.*)' + endID, content)
	if PUB_ID != None:
		return PUB_ID.group(1)
	else:
		return None


'''
Récupère le PUB_hash
dans le contenu passé en argument.
S'il n'y en a pas, retourne None,
sinon retourne le PUBId (en string).
S'il y en a plusieurs, il retourne le dernier.

@param content : String
			  le contenu dans lequel trouver l'id.
'''
def getPUBHash(content):
	PUB_hash = re.search(beginHash + '(.*)' + endHash, content)
	if PUB_hash != None:
		return PUB_hash.group(1)
	else:
		return None


'''
Génère le hash d'une entrée en supprimant tout 
d'abord les metainfos de l'entrée puis le retourne.

@param entry : String
			  l'entrée pour laquelle générer un hash.
'''
def generateHash(entry):
	return hashlib.md5(removeHash(entry).encode()).hexdigest()


'''
Enlève les métadonnées d'une entrée.

@param entry : String
			  l'entrée pour laquelle supprimer les métadonnées.
'''
def removeHash(entry):
	return entry.split(entryMetaInfo)[0]


'''
Récupère tous les PUB_id
dans le contenu passé en argument.
(Un PUB_id a la forme suivante :
"<!-- PUB_id = &beginID&69&endID& -->")
S'il n'y en a pas, retourne un tableau vide.

@param content : String
			  le contenu dans lequel trouver les ids.
'''
def getAllPUBIds(content):
	return re.findall(beginID + '(.*)' + endID, content)


'''
Cette fonction va s'occuper d'aller sur la page
indiquée en argument et regarder si elle trouve le bloc
de méta information de PUB (bloc commençant par 
"<!-- PUB METAINFOS :").
Si ce bloc de méta info
est présent, elle va retourner l'Id qui y 
est contenu (représentant le dernier Id attribué
à une entrée de page).
Si ce bloc de méta info n'est pas présent,
cette fonction va s'occuper de le créer,
y mettre comme valuer d'ID 0, puis retourner
0.
Si une quelquonque erreur s'est produite,
la fonction retournera un chiffre négatif
ou bien enverra une exception (comme vous le sentez)
'''
def fetchPUBmetaInfo(initialPass):
	if initialPass:
		currentID = '0'
		#écrire metainfo dans le HUB
		newMetaInfo = metaInfo +titleID+ beginID + currentID + endID+endEntryMetaInfo
		newContent = newMetaInfo + '\n'
		payload={'action':'edit','assert':'user','format':'json','utf8':'','prependtext':newContent,'summary':summary,'title':user,'token':edit_token}
		r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)
	else:
		HUBcontent = fetchPageData(user)
		result = getPUBId(HUBcontent)
		if result == None:
			#la balise a été effacée/endommagée
			currentID = '-1'
		else:
			currentID = result
	return currentID


'''Cette fonction doit être appelée après que 
PUB ait fait toute sa traversée, elle doit
actualiser l'ID contenu de méta_info.

@param newId : Int 
				Le nouvel ID a inscrire dans les metaInfo.
'''
def updatePUBmetaInfo(newId):
	result=requests.post(baseurl+'api.php?action=query&titles='+user+'&export&exportnowrap')
	soup=BeautifulSoup(result.text,'html.parser')
	content=''
	for primitive in soup.findAll("text"):
		content+=primitive.string
	currentID = fetchPUBmetaInfo(False)
	content=content.replace(metaInfo + beginID + currentID + endID+endEntryMetaInfo, metaInfo + beginID + str(newId) + endID+endEntryMetaInfo)
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
def getPageList():
	protected_logins=["Frederickaplan","Maud","Vbuntinx","Testbot","IB","SourceBot","PageUpdaterBot","Orthobot","BioPathBot","ChronoBOT","Amonbaro","AntoineL","AntoniasBanderos","Arnau","Arnaudpannatier","Aureliver","Brunowicht","Burgerpop","Cedricviaccoz","Christophe","Claudioloureiro","Ghislain","Gregoire3245","Hirtg","Houssm","Icebaker","JenniCin","JiggyQ","JulienB","Kl","Kperrard","Leandro Kieliger","Marcus","Martin","MatteoGiorla","Mireille","Mj2905","Musluoglucem","Nacho","Nameless","Nawel","O'showa","PA","Qantik","QuentinB","Raphael.barman","Roblan11","Romain Fournier","Sbaaa","Snus","Sonia","Tboyer","Thierry","Titi","Vlaedr","Wanda"]
	depuis_date = '2017-02-02T16:00:00Z'

	liste_pages=[]
	for user in protected_logins:
		result=requests.post(baseurl+'api.php?action=query&list=usercontribs&ucuser='+user+'&format=xml&ucend='+depuis_date)
		soup=BeautifulSoup(result.content,'lxml')
		for primitive in soup.usercontribs.findAll('item'):
			liste_pages.append(primitive['title'])

	return list(set(liste_pages))


'''
À l'aide du titre de la page donné en argument,
récupère les données de cette page, 
sous la forme d'une string

@param pageName : String
				le titre de la page wikipast où aller chercher les données.
'''
def fetchPageData(pageName):
	result=requests.post(baseurl+'api.php?action=query&titles='+pageName+'&export&exportnowrap')
	soup=BeautifulSoup(result.text, "lxml")
	pageData=''
	for primitive in soup.findAll("text"):
		if primitive.string != None:
			pageData+=primitive.string
	return pageData


'''
Vérifie que l'entrée donnée en argument soit bien une 
entrée biographie (c'est à dire une entrée à puce commencant par une date)
@param entre : String
				l'entrée à vérifier.
'''
def isValidEntry(entry):
	if entry[0:3] == '*[[' and (entry[3:7]+entry[8:10]+entry[11:13]).isdigit() and entry[7]+entry[10] == '..' and entry[13:15] == ']]':
		return True
	else:
		return False


'''
Va s'occuper de trier le contenu
de la page donné en argument
pour en ressortir que les entrées biographiques
sourcées (le texte ajouté autre part est ignoré).
Une entrée est normalement écrite sous la forme (dans le code):
*[[YYYY.MM.JJ]] / [[<lieu>]]. [[<évènement>]] entre [[<Mr. X>]] et [[<Mr.Y>]]. [<référence>]

!! remarque importante que je n'avais pas pensé avant :
Où met-on le PUB_id ? (il sera de la forme "<!-- PUB_id=69-->") ?
Il faut penser qu'on doit le mettre dans un endroit stratégique,
car il faudrait que si d'autres bots reprennent ou modifient des entrées,
ils conservent l'intégrité du PUB_id.

Cette fonction retournera une liste de String qui constituent
les entrées retournées sous la forme montrée plus haut.

@param content : String
				le contenu de la page
'''
def parseEntries(content):
	lines = content.split('\n')
	newLines = []
	foundOne = False
	for line in lines:
		if isValidEntry(line):
			newLines.append(line)
			foundOne = True
		else:
			if foundOne:
				return newLines
	return newLines



'''
Va mettre à jour les valeurs entre les balises (id et hash) de l'entrée

@param entry : String
			  l'entrée biographie.
@param PUBhash : string 
				hash à mettre à jour 
@param PUBId : Int
			  l'Id à mettre à jour sur cette page.
'''
def setPUBInfos(entry,PUBId,PUBhash):
	entry = removeHash(entry)
	return entry+entryMetaInfo+titleID+beginID+PUBId+endID+titleHASH+beginHash+PUBhash+endHash+endEntryMetaInfo


'''
retourne une liste d'hyperLinks contenu
dans cette entrée sous une forme de liste 
de String, mais en excluant de cette liste l'argument
toExclude.
'''
def getHyperLinks(entry, toExclude):
	hyperLinks = re.findall('\[\[(.*?)\]\]', entry)
	hyperLinks = set([x.split('|')[0] for x in hyperLinks])
	if toExclude in hyperLinks: hyperLinks.remove(toExclude)
	return list(hyperLinks)


'''
retourne une liste d'hyperLinks contenu
dans cette entrée sous une forme de liste 
de String, mais en excluant de cette liste l'argument
toExclude.
'''
def getReferences(entry):
	return re.findall('\[(.*?)\]', entry)


'''
Va créer une nouvelle page wikipast nommée selon 
l'argument donné. Si cette page existe déjà, va 
simplement retourner l'URL de la page. Autrement retourne
l'url de cette pas nouvelle créée.

@oaram name : String
			  Le nom de la page à créer.
'''
def createNewPage(name):
	subtitleToAdd = ''
	payload={'action':'edit','assert':'user','format':'json','utf8':'','prependtext':subtitleToAdd,'summary':summary,'title':name,'token':edit_token}
	r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)


'''
Teste si la page donnée en argument existe déjà.

@oaram name : String
			  Le nom de la page à tester.
@oaram name : List(String)
			  La liste des pages existantes.
'''
def isNewPage(name, listOfPagesToCompare):
	return not (name in listOfPagesToCompare)
	


'''
Détermine si deux entrées sont identiques.
Pour ce faire on teste que
les dates, les lieux et la liste des hypermots
sont identiques.
(Pas de comparaison entre les PUBId!)
Si toutes les conditions énumérées ci dessus
sont satisfaites, alors on renvoit True,
autrement Talse.

@param entry1 : String
				La première entrée à comparer
@param entry2 : String
				La seconde entrée avec laquelle on compare la première
'''
def areEntrySimilar(entry1, entry2):
	#la liste des hypermots inclus également la date
	listOfHyperLinks1 = getHyperLinks(entry1, '')
	listOfHyperLinks2 = getHyperLinks(entry2, '')
	listOfReferences1 = getReferences(entry1)
	listOfReferences2 = getReferences(entry2)
	
	return (listOfHyperLinks1 == listOfHyperLinks2) and (listOfReferences1 == listOfReferences2)


'''
Va transformer une liste d'entrée
en un format que la page wikipédia en une seule
sting et retourner donc ces entrées
formatée en un seul bloc

@param entries : List(String)
				Les entrées nouvellement modifiées
'''
def unParseEntries(entries):
	if entries:
		return '\n'.join(entries)
	else:
		return None


'''
Va uploader le contenu nouvellement modifié
sur la page indiqué par le titre de la page

@param previousContent : String
				le contenu précédent
@param newContent : String
				le contenu à uploader
@param pageName : String
				Le nom de la page où appliquer ces modifications.

'''
def uploadModifications(previousContent, newContent, pageName):
	result=requests.post(baseurl+'api.php?action=query&titles='+pageName+'&export&exportnowrap')
	soup=BeautifulSoup(result.text,'html.parser')
	content=''
	for primitive in soup.findAll("text"):
		if primitive.string != None:
			content+=primitive.string
	if newContent == None :
		newContent = ''
	if previousContent == None :
		payload={'action':'edit','assert':'user','format':'json','utf8':'','prependtext':newContent+'\n','summary':summary,'title':pageName,'token':edit_token}
	else:
		content=content.replace(previousContent, newContent)
		payload={'action':'edit','assert':'user','format':'json','utf8':'','text':content,'summary':summary,'title':pageName,'token':edit_token}
	r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)


if(sys.argv[1] == 'clean'):
	cleaner()
else:
	pass
	#main()
