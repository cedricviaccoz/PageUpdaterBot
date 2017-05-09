# Résumé des fonctionnalités 
*PageUpdaterBot* est un robot qui s'occupe de compléter les différentes pages sur Wikipast à partir d'hyperliens. *PageUpdaterBot* vérifie que sur chaque page, tous les hyperliens (excepté les dates) mènent vers une page existante et que les entrées correspondantes existent et soient placées aux bons endroits.  Si la page associée à l'hyperlien n'existe pas, *PageUpdaterBot* crée la page et place l'entrée associée dans cette page. 

# Description technique 
*PageUpdaterBot* va analyser le contenu de la page entrée par entrée. Pour chaque entrée, le bot extrait les hyperliens qu'elle contient, en excluant la date et celui de la page en cours d'analyse. *PageUpdaterBot* va ensuite vérifier que chaque hyperlien redirige vers une page existante, que l'entrée existe bien dans cette page et qu'elle est placée au bon endroit. Si l'un de ces trois critères n'est pas remplis, *PageUpdaterBot* va créer la page, ajouter l'entrée, ou réordonner chronologiquement les entrées. Afin de faciliter le traitement, un ''PUB_id'' est associé à chaque entrée sous la forme d'un commentaire `<!-- PUB METAINFOS : entryID = &beginID&42&endID& entryHash = &beginHASH&6936b65604c6f91fab6552c2b2bdad9a&endHASH& -->` placé à la fin de la ligne. 

Une des principales fonctions de *PageUpdaterBot* est de répercuter les modifications faites sur une page particulière sur toutes les autres pages concernée par l'entrée. Le cas où des entrées seraient présentes sous des formes différentes sur deux pages est donc pris en charge. Pour vérifier que les entrées sont les mêmes, leurs ''PUB_id'' sont comparés. Pour déterminer quelle entrée a été modifiée en dernier, un hash de l'entrée est ajouté au ''PUB_id''. Si le hash de l'entrée ne correspond plus à celui stocké, c'est que cette ligne à été modifiée. C'est donc cette entrée qui sera copiée sur toutes les pages. Si les deux entrées sont modifiées, la première que rencontre le bot sera conservée. Si une entrée de la page mère n'a pas de ''PUB_id'', l'algorithme lui en donnera un. Si une entrée de la page fille ne possédait pas de ''PUB_id'', la liste d'hyperliens et de références qu'elle contient est comparée avec toutes celle de la page mère. Si une correspondance est trouvée, les ''PUB_id'' correspondants seront ajoutés. 

# Discussion 

## Performances 
L'algorithme possède une complexité en O(n^2). En effet, *PageUpdaterBot* compare toutes les entrées de la page mère avec toutes celles de la page fille. Le bot a des performances raisonnables compte tenu du faible nombre de pages contenu sur  *WikiPast*.

## Limites du bot
Le traitement que peut être source d'erreur si un utilisateur maladroit modifie accidentellement le ''PUB_id'' à la fin de chaque entrée, ce qui rend ce bot vulnérable au mauvais comportement des utilisateurs. Il serait envisageable d'ajouter une sorte de "checksum" pour contrôler si le commentaire a été affecté par un utilisateur et dans ce cas recommencer la construction des IDs à partir de zéro. De plus, dans le cas où une section contiendrait des entrées sous forme de liste, puis quelques paragraphes de textes, et enfin à nouveau une liste d'entrée, seul la première liste d'entrée sera prise en charge.

# Exemples 
### Exemple 1
Un utilisateur met à jour la page [[Henri Dunant]] et entre l'information suivante :

*[[1864.08.22]] / [[Genève]]. [[Création]] par [[Henri Dunant]] de la [[Croix rouge]]. [http://letemps.archives.world/page/JDG_1897_12_31/1/%22Henri%20Dunant%22]

En admettant que l'entrée n'est pas encore présente dans [[Genève]], [[Création]] et que la page [[Croix rouge]] n'existe pas, le bot commence par associer un ''PUB_id'' à la nouvelle entrée et copie la ligne dans la page [[Genève]] ainsi que [[Création]]. Le bot trie chronologiquement les entrées dans chacune des 2 pages. L'entrée se retrouve donc à la bonne place. Comme la page [[Croix Rouge]] n'existe pas, le bot crée la page et recopie la ligne dans cette nouvelle page. Finalement, les entrées de la page [[Henri Dunant]] sont ordonnées chronologiquement.

De plus, un hash est associé à chacune des entrées afin de détecter une quelconque modification et ainsi mettre à jour les pages qui y sont référencées.

### Exemple 2

Un utilisateur met à jour la page [[Création]] et supprime l'information suivante :

*[[1864.08.22]] / [[Genève]]. [[Création]] par [[Henri Dunant]] de la [[Croix rouge]]. [http://letemps.archives.world/page/JDG_1897_12_31/1/%22Henri%20Dunant%22](référence

Le bot supprime l'entrée dans les pages [[Croix rouge]], [[Henri Dunant]] et [[Genève]] en détectant qu'un id est associé à une entrée dans ces 3 pages mais pas dans la page [[Création]].
