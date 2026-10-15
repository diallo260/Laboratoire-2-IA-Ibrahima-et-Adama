# Laboratoire 2 - Partie 1 : Algorithme A* sur le 8-puzzle

Travail réalisé par : Diallo Ibrahima (DIAI01100203) et Adama A Balde ( )
Langage utilisé : Python 3.14.2

Lancement du programme : se positionner dans le dossier `Partie1_Astar` et taper `python main.py`

Le programme lit les 4 puzzles du dossier `Entree`, lance A* 10 fois avec chacune des deux heuristiques,
puis affiche un résumé. On peut aussi tester un seul puzzle en tapant : `python main.py Entree/Ex1-1.txt`

## Organisation des fichiers

- `puzzle.py` : lecture d'un puzzle, déplacements possibles de la case vide et test de solubilité.
- `heuristiques.py` : les deux heuristiques h1 et h2.
- `astar.py` : l'algorithme A*.
- `main.py` : lance les exécutions et enregistre les résultats.
- `Entree` : les 4 puzzles de départ (identiques à ceux utilisés au laboratoire 1).
- `Resultats` : un fichier par exécution, 80 au total.
- `Chemins` : la suite des déplacements trouvée pour chaque puzzle.

Nous avons gardé les mêmes puzzles que ceux du laboratoire 1 pour pouvoir comparer A* avec le BFS et l'IDDFS sur exactement les mêmes cas.

## Principe d'A*

À chaque itération, A* choisit dans la frontière l'état qui a la plus petite valeur
de f(n) = g(n) + h(n).
- g(n) est le nombre de déplacements déjà faits depuis l'état initial (le départ).
- h(n) est une estimation du nombre de déplacements qui restent, autrement dit l'heuristique.

A* commence donc par les états qui semblent les plus proches de l'objectif au lieu de tout explorer niveau par niveau comme le fait le BFS.

## Spécification des heuristiques utilisées

- h1 : nombre de tuiles mal placées. On compte les tuiles qui ne sont pas à leur place
  finale (la case vide n'est pas comptée). Chaque tuile mal placée devra
  bouger au moins une fois, donc h1 ne surestime jamais le nombre de coups restants.
- h2 : distance de Manhattan. Pour chaque tuile, on compte le nombre de lignes et
  de colonnes qui la séparent de sa place finale, puis on fait la somme. Un déplacement ne rapproche
  qu'une seule tuile d'une seule case, donc h2 ne surestime jamais lui aussi.

Les deux heuristiques sont donc admissibles, ce qui permet de garantir qu'A* trouve toujours le chemin
le plus court. De plus, h2 est toujours supérieure ou égale à h1 (une tuile mal placée est à au moins une case de sa vraie place), c'est ce qui
permet de dire que h2 domine h1.
Elle est plus proche de la réalité et devrait guider A* de manière plus efficace.

Si nous prenons par exemple le puzzle Ex1-1, h1 = 6 et h2 = 14, alors que la vraie solution demande
20 déplacements.

- Remarque : le cours mentionne aussi qu'on peut combiner deux heuristiques admissibles
avec h3 = max(h1, h2), qui reste admissible et domine les deux. Nous ne l'avons pas
ajoutée, car pour le 8-puzzle h2 est toujours supérieure ou égale à h1 : on a donc
toujours max(h1, h2) = h2. Nous l'avons vérifié, et A* avec max(h1, h2) fait exactement
le même nombre d'itérations qu'avec h2 (par exemple 283 sur Ex1-1).

## Contenu des fichiers de résultats

Chaque fichier du dossier `Resultats` correspond à une exécution et suit le même format que celui du laboratoire 1. Chaque ligne d'itération contient :
1. le numéro de l'itération ;
2. la taille de la liste des états explorés ;
3. la taille de la frontière ;
4. le nombre total d'états générés depuis le début.

L'avant-dernière ligne donne le nombre total d'itérations et la dernière ligne donne le temps
d'exécution en secondes.

La taille de la liste des états explorés augmente de 1 à chaque itération,
car A* développe exactement un état par itération. C'est pour cela que nous avons aussi ajouté la frontière
et les états générés, ce qui permet de mieux montrer le travail fait.

## Résultats (moyenne sur 10 exécutions)

| Puzzle | Heuristique | Coups | Itérations | États générés | Temps moyen (s) |
|---|---|---|---|---|---|
| Ex1-1 | h1 | 20 | 3 667 | 5 751 | 0,0300 |
| Ex1-1 | h2 | 20 | 283 | 452 | 0,0051 |
| Ex1-2 | h1 | 17 | 984 | 1 605 | 0,0081 |
| Ex1-2 | h2 | 17 | 233 | 373 | 0,0019 |
| Ex1-3 | h1 | échec | 181 440 | 181 440 | 1,3977 |
| Ex1-3 | h2 | échec | 181 440 | 181 440 | 1,3651 |
| Ex1-4 | h1 | 28 | 68 754 | 90 639 | 0,5335 |
| Ex1-4 | h2 | 28 | 727 | 1 085 | 0,0044 |

Les 10 exécutions d'un même cas donnent toujours le même nombre d'itérations et le même chemin :
l'algorithme ne fait aucun choix au hasard. Seul le temps change un peu d'une exécution à l'autre. C'est pour cela
que nous avons fait la moyenne.

## Observations

A* trouve toujours la solution la plus courte. Il trouve 20, 17 et 28 coups, exactement comme le BFS et l'IDDFS du laboratoire 1.

h2 est beaucoup plus efficace que h1. Sur Ex1-1, h2 fait 13 fois moins d'itérations que h1. Sur Ex1-4, le puzzle le plus long, l'écart monte à 95 fois
moins (727 contre 68 754). Plus le puzzle est difficile, plus une bonne heuristique fait la différence.

A* explore beaucoup moins d'états que les recherches non informées. Sur Ex1-1, le BFS du laboratoire 1 parcourait
61 757 états et l'IDDFS 201 154, alors qu'A* avec h2 n'en génère que 452 pour trouver la même solution.

Sur un puzzle sans solution, l'heuristique n'aide pas. Ex1-3 n'a pas de solution.
A* doit quand même vérifier les 181 440 états atteignables avant de conclure, avec h1 comme avec h2. Le programme indique d'ailleurs dès le départ que ce puzzle
est insoluble grâce au test de parité. A* reste tout de même plus rapide que l'IDDFS du laboratoire 1 sur ce cas (1,4 s contre 48 s).

## Conclusion

Le choix de l'heuristique change complètement le coût de la recherche. Avec h2,
A* trouve la meilleure solution en explorant seulement quelques centaines d'états,
là où les algorithmes non informés en parcouraient des dizaines de milliers.