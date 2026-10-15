# genetique.py - Algorithme génétique pour le Sudoku

# On fait évoluer une population de grilles, génération après génération,
# en s'inspirant de la sélection naturelle : les meilleures grilles ont plus
# de chances d'avoir des « enfants », et les enfants mélangent les qualités
# de leurs deux parents.

# Individu : une grille complète où chaque bloc 3x3 contient les chiffres 1 à 9
           # (voir sudoku.py). Les cases données par le puzzle ne changent jamais.

# Fitness  : le nombre de conflits dans les lignes et les colonnes.
         #  Plus il est petit, meilleur est l'individu. 0 = solution.

# Sélection des parents : par tournoi. On tire 3 individus au hasard et celui
         # qui a le moins de conflits devient parent.

# Crossover : par bandes. Chaque couple de parents donne 2 enfants :
          # - enfant 1 : pour chacune des 3 bandes horizontales (3 blocs côte
           #  à côte), il prend celle du parent dont les 3 lignes ont le moins
           #  de conflits ;
         #  - enfant 2 : même idée avec les 3 bandes verticales (colonnes).
          # Les blocs sont copiés en entier, donc l'enfant reste valide.

# Mutation : on échange deux cases non fixes d'un même bloc. On refuse un échange
         # qui placerait un chiffre dans une ligne ou une colonne où le puzzle
          # le donne déjà.

# Élitisme : les NB_ELITES meilleurs individus passent tels quels à la génération
          #  suivante, pour ne jamais perdre la meilleure grille.

# Redémarrage : si la meilleure grille ne s'améliore plus pendant MAX_STAGNATION
          # générations, la population est devenue trop semblable. On la remplace
          # ENTIÈREMENT par de nouvelles grilles au hasard. Dans nos essais, garder
          # même un seul ancien individu ramenait toute la population au même
          # blocage.

 # Une itération = une génération.


import time

import numpy as np

from sudoku import conflits_population, cases_libres_par_bloc

# Paramètres de l'algorithme (choisis après plusieurs essais)
TAILLE_POPULATION = 200   # nombre de grilles dans la population
TAILLE_TOURNOI = 3        # nombre d'individus tirés à chaque tournoi
TAUX_CROISEMENT = 0.9     # probabilité de croiser deux parents (sinon on les copie)
TAUX_MUTATION = 0.8       # probabilité qu'un enfant subisse une mutation
NB_ELITES = 10            # nombre de meilleurs individus gardés à chaque génération
MAX_STAGNATION = 60       # générations sans progrès avant un redémarrage
MAX_GENERATIONS = 10000   # nombre maximum de générations par exécution



# Création des individus.

def _interdits(grille):

    # Pour chaque case (r, c), donne les chiffres déjà DONNÉS par le puzzle dans
    # sa ligne ou sa colonne. Placer un de ces chiffres dans la case créerait
    # forcément un conflit, donc on essaie de les éviter.

    lignes = [set(grille[r][grille[r] != 0].tolist()) for r in range(9)]
    colonnes = [set(grille[:, c][grille[:, c] != 0].tolist()) for c in range(9)]
    return [[lignes[r] | colonnes[c] for c in range(9)] for r in range(9)]


def _individu_aleatoire(grille, blocs_libres, interdits, rng):

    # Crée une grille au hasard pour la population : chaque bloc est complété
    # avec ses chiffres manquants. Pour chaque case, on choisit si possible un
    # chiffre qui n'est pas déjà donné dans sa ligne ou sa colonne.

    ind = grille.copy()
    for libres in blocs_libres:
        if not libres:
            continue # bloc entièrement donné par le puzzle.
        r0, c0 = 3 * (libres[0][0] // 3), 3 * (libres[0][1] // 3)
        bloc = ind[r0:r0 + 3, c0:c0 + 3]
        restants = list(set(range(1, 10)) - set(bloc[bloc != 0].tolist()))  # chiffres à placer
        ordre = list(libres)
        rng.shuffle(ordre) # on remplit les cases dans un ordre au hasard.
        for (r, c) in ordre:
            permis = [v for v in restants if v not in interdits[r][c]]
            # Si aucun chiffre n'est « permis », on en prend un au hasard quand même
            v = permis[rng.integers(len(permis))] if permis else restants[rng.integers(len(restants))]
            ind[r, c] = v
            restants.remove(v)
    return ind



# Opérateurs génétiques : sélections, crossover et mutation.


def _tournoi(couts, nb_parents, rng):

    # Sélection par tournoi, faite pour tous les parents d'un coup :
    # pour chaque parent à choisir, on tire TAILLE_TOURNOI individus au hasard
    # et on garde celui qui a le moins de conflits. Retourne leurs positions.

    candidats = rng.integers(0, len(couts), size=(nb_parents, TAILLE_TOURNOI))
    gagnants = np.argmin(couts[candidats], axis=1)
    return candidats[np.arange(nb_parents), gagnants]


def _conflits_par_ligne_colonne(pop):
    # Nombre de doublons de chaque ligne et de chaque colonne, pour chaque individu.
    trie_l = np.sort(pop, axis=2)
    trie_c = np.sort(pop, axis=1)
    par_ligne = np.count_nonzero(trie_l[:, :, 1:] == trie_l[:, :, :-1], axis=2)
    par_colonne = np.count_nonzero(trie_c[:, 1:, :] == trie_c[:, :-1, :], axis=1)
    return par_ligne, par_colonne


def _croisement(parents_a, parents_b, rng):

    # Crossover par bandes, fait pour tous les couples en même temps.
    # Retourne 2 enfants par couple de parents.

    n = len(parents_a)
    # Conflits de chaque bande : on additionne les conflits des 3 lignes
    # (ou des 3 colonnes) qui forment la bande.
    la, ca = _conflits_par_ligne_colonne(parents_a)
    lb, cb = _conflits_par_ligne_colonne(parents_b)
    bande_la, bande_lb = la.reshape(n, 3, 3).sum(2), lb.reshape(n, 3, 3).sum(2)
    bande_ca, bande_cb = ca.reshape(n, 3, 3).sum(2), cb.reshape(n, 3, 3).sum(2)
    # Pour chaque bande, on prend celle du parent B si elle est meilleure.
    # En cas d'égalité, on tire à pile ou face.
    hasard_l = rng.random((n, 3)) < 0.5
    hasard_c = rng.random((n, 3)) < 0.5
    prendre_b_l = (bande_lb < bande_la) | ((bande_lb == bande_la) & hasard_l)   # (n, 3)
    prendre_b_c = (bande_cb < bande_ca) | ((bande_cb == bande_ca) & hasard_c)
    # On transforme le choix « par bande » en choix « par case » pour copier la grille
    masque_l = np.repeat(prendre_b_l, 3, axis=1)[:, :, None]                    # bandes horizontales
    masque_c = np.repeat(prendre_b_c, 3, axis=1)[:, None, :]                   # bandes verticales
    enfants_1 = np.where(masque_l, parents_b, parents_a)
    enfants_2 = np.where(masque_c, parents_b, parents_a)

    # Dans 10 % des cas (1 - TAUX_CROISEMENT), pas de croisement : les enfants
    # sont de simples copies des parents
    sans = rng.random(n) >= TAUX_CROISEMENT
    enfants_1[sans] = parents_a[sans]
    enfants_2[sans] = parents_b[sans]
    return np.concatenate([enfants_1, enfants_2])


def _mutation(enfants, paires, interdit, rng, essais=10):

   # Mutation de certains enfants : échange de deux cases libres d'un même bloc.
    #  paires   : liste de tous les échanges possibles (r1, c1, r2, c2)
    #  interdit : interdit[r, c, v] vaut True si le chiffre v est déjà donné
    # par le puzzle dans la ligne r ou la colonne c
    # Pour chaque enfant muté, on tire jusqu'à 10 échanges au hasard et on fait
    # le premier qui est permis. Si aucun ne l'est, l'enfant reste tel quel.
    # Tout est fait avec numpy pour traiter tous les enfants en même temps.

   # On choisit au hasard les enfants qui vont muter
    mutes = np.nonzero(rng.random(len(enfants)) < TAUX_MUTATION)[0]
    if len(mutes) == 0:
        return

   # Pour chacun, on tire 10 échanges possibles au hasard
    tirages = paires[rng.integers(0, len(paires), size=(len(mutes), essais))]   # (m, essais, 4)
    r1, c1, r2, c2 = (tirages[..., k] for k in range(4))
    ind = mutes[:, None]
    v1 = enfants[ind, r1, c1]
    v2 = enfants[ind, r2, c2]

   # Un échange est permis si aucun des deux chiffres n'arrive dans une ligne
   # ou une colonne où le puzzle le donne déjà
    legal = ~interdit[r1, c1, v2] & ~interdit[r2, c2, v1]                       # (m, essais)
    a_un_legal = legal.any(axis=1)
    choix = np.argmax(legal, axis=1) # position du premier échange permis                                             # 1er échange légal

   # On applique l'échange choisi aux enfants qui en ont un
    m = np.nonzero(a_un_legal)[0]
    j = choix[m]
    i = mutes[m]
    r1, c1, r2, c2 = r1[m, j], c1[m, j], r2[m, j], c2[m, j]
    v1, v2 = v1[m, j], v2[m, j]
    enfants[i, r1, c1] = v2
    enfants[i, r2, c2] = v1



# Algorithme Principale


def genetique(grille, fixes, rng, max_generations=MAX_GENERATIONS):
    debut = time.perf_counter()
    # Préparation (fait une seule fois)
    # Chiffres interdits pour chaque case, sous deux formes :
    # une liste d'ensembles (pour créer les individus) et un tableau
    # numpy de True/False (pour la mutation, plus rapide)
    interdits = _interdits(grille)
    interdit = np.zeros((9, 9, 10), dtype=bool)
    for r in range(9):
        for c in range(9):
            interdit[r, c, list(interdits[r][c])] = True
    # Tous les échanges possibles entre deux cases libres d'un même bloc
    blocs_libres = cases_libres_par_bloc(fixes)
    paires = np.array([(*b[i], *b[j]) for b in blocs_libres
                       for i in range(len(b)) for j in range(i + 1, len(b))])
    nb_enfants = TAILLE_POPULATION - NB_ELITES # le reste de la population après les meilleurs.

    def individus_aleatoires(n):
        return np.array([_individu_aleatoire(grille, blocs_libres, interdits, rng)
                         for _ in range(n)])

# Population de départ
    population = individus_aleatoires(TAILLE_POPULATION)
    couts = conflits_population(population) # fitness de chaque individu

    meilleur_cout = int(couts.min())
    meilleur_individu = population[np.argmin(couts)].copy()  # meilleure grille jamais vue
    stagnation = 0      # nombre de générations sans amélioration
    redemarrages = 0
    trace = []          # une ligne par génération : (génération, meilleur, moyenne, redémarrages)
    generation = 0

# Boucle des générations.
    while meilleur_cout > 0 and generation < max_generations:
        generation += 1

        # 1. Élitisme : on met de côté les meilleurs individus
        elites = population[np.argsort(couts)[:NB_ELITES]]

        # 2. Sélection des parents par tournoi, crossover, puis mutation
        nb_couples = (nb_enfants + 1) // 2
        parents_a = population[_tournoi(couts, nb_couples, rng)]
        parents_b = population[_tournoi(couts, nb_couples, rng)]
        enfants = _croisement(parents_a, parents_b, rng)[:nb_enfants]
        _mutation(enfants, paires, interdit, rng)

        # 3. Nouvelle génération = élites + enfants
        population = np.concatenate([elites, enfants])
        couts = conflits_population(population)

        # 4. A-t-on progressé ? Sinon, on compte la stagnation
        if int(couts.min()) < meilleur_cout:
            meilleur_cout = int(couts.min())
            meilleur_individu = population[np.argmin(couts)].copy()
            stagnation = 0
        else:
            stagnation += 1
            if stagnation >= MAX_STAGNATION:
                # Population bloquée : on repart d'une population entièrement nouvelle
                redemarrages += 1
                stagnation = 0
                population = individus_aleatoires(TAILLE_POPULATION)
                couts = conflits_population(population)

        trace.append((generation, int(couts.min()), float(couts.mean()), redemarrages))

 # Résultats.
    return {
        "trouve": meilleur_cout == 0,
        "etat": meilleur_individu,
        "iterations": generation,
        "redemarrages": redemarrages,
        "meilleur_cout": meilleur_cout,
        "trace": trace,
        "temps": time.perf_counter() - debut,
    }