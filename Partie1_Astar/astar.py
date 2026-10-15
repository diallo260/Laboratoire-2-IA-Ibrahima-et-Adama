# astar.py - L'algorithme A*

# A* choisit toujours dans la frontière l'état qui a le plus petit
# f(n) = g(n) + h(n) :
  # g(n) : nombre de coups déjà faits depuis l'état de départ (1 par mouvement)
  # h(n) : estimation du nombre de coups qui restent (heuristique h1 ou h2)

# On garde deux listes, comme vu en cours :
  # - la frontière : les états trouvés mais pas encore développés.
    # On utilise une file de priorité (heapq) qui donne toujours
    # l'état avec le plus petit f en premier.
  # - les explorés : les états déjà développés. Ils évitent de tourner en rond
   #  en revenant sur un état déjà traité.

# Une itération = on retire le meilleur état de la frontière, on regarde
# si c'est l'objectif, sinon on ajoute ses voisins à la frontière.


import heapq
import itertools
import time

from puzzle import ETAT_OBJECTIF, successeurs


def astar(etat_initial, heuristique):
    debut = time.perf_counter() # pour mesurer le temps d'exécution

    # Initialisation :
    # Chaque élément de la frontière est un tuple (f, g, compteur, état).
    # Python trie les tuples élément par élément : d'abord f, puis g, puis le
    # compteur. Le compteur sert à départager deux états qui ont le même f et
    # le même g : le premier arrivé sort en premier.
    compteur = itertools.count()  # départage les égalités de f (ordre FIFO)
    frontiere = [(heuristique(etat_initial), 0, next(compteur), etat_initial)]

    meilleur_g = {etat_initial: 0}         # plus petit cout connu pour atteindre chaque etat.
    parent = {etat_initial: (None, None)}  # pour chaque etat : état d'avant et mouvement fait)
    explores = set()

    trace = []          # une ligne par itération, écrire ensuite dans le fichier de résultats
    iteration = 0
    etats_generes = 1   # l'état initial compte comme un état généré

# Boucle Principale :
    while frontiere:
        # On retire l'état le plus fiable.
        f, g, _, etat = heapq.heappop(frontiere)

        # Un même état peut se retrouver plusieurs fois dans la frontière
        # (heapq ne permet pas de retirer un élément). Si on l'a déjà
        # développé, cette copie est inutile : on l'ignore.
        if etat in explores:
            continue

        iteration += 1
        explores.add(etat)

# test de l'objectif : on a trouvé la solution.
        if etat == ETAT_OBJECTIF:
            trace.append((iteration, len(explores), len(frontiere), etats_generes))
            return {
                "trouve": True,
                "chemin": _reconstruire_chemin(parent, etat),
                "iterations": iteration,
                "etats_generes": etats_generes,
                "trace": trace,
                "temps": time.perf_counter() - debut,
            }
# Développement : on ajoute les voisins à la frontière.
        for action, voisin in successeurs(etat):
            if voisin in explores:
                continue # déjà traité, il est inutile d'y revenir.
            nouveau_g = g + 1

            # On garde ce voisin seulement si ce chemin est plus court
            # que tous ceux trouvés jusqu'ici pour l'atteindre
            if nouveau_g < meilleur_g.get(voisin, float("inf")):
                meilleur_g[voisin] = nouveau_g
                parent[voisin] = (etat, action)
                heapq.heappush(
                    frontiere,
                    (nouveau_g + heuristique(voisin), nouveau_g, next(compteur), voisin),
                )
                etats_generes += 1
# On note la taille des listes à la fin de cette itération.
        trace.append((iteration, len(explores), len(frontiere), etats_generes))

    # Frontière vide : aucune solution, tous les états ont été visités, pas de solution.
    return {
        "trouve": False,
        "chemin": [],
        "iterations": iteration,
        "etats_generes": etats_generes,
        "trace": trace,
        "temps": time.perf_counter() - debut,
    }


def _reconstruire_chemin(parent, etat):

   # Retrouve la suite des mouvements de la solution.
   # On part de l'objectif et on remonte d'état en état grâce au dictionnaire
   # parent, jusqu'à l'état de départ. On inverse ensuite la liste pour avoir
   # les mouvements dans le bon ordre.

    actions = []
    while parent[etat][0] is not None:
        etat_precedent, action = parent[etat]
        actions.append(action)
        etat = etat_precedent
    actions.reverse()
    return actions