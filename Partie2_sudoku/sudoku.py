# sudoku.py - Représentation du Sudoku (commune aux deux algorithmes)

# Ce fichier contient les outils utilisés à la fois par le hill climbing et par
# l'algorithme génétique : lire un puzzle, l'afficher, créer une grille de
# départ, compter les conflits et vérifier une solution.

# Grille : tableau numpy 9x9 d'entiers, 0 = case vide.
# Fixes  : tableau 9x9 de True/False. True = case donnée par le puzzle,
# qu'on n'a jamais le droit de modifier.

# Notre idée de départ :
# On part du puzzle donné (ses cases fixes ne changent jamais) et on remplit
# ses cases vides au hasard, de façon que chaque bloc 3x3 contienne les
# chiffres de 1 à 9 une seule fois. On obtient une grille complète, mais
# pleine de conflits dans les lignes et les colonnes. C'est ce que fait toute
# recherche locale : partir d'un état complet et l'améliorer petit à petit.

# Mesure de la qualité d'une grille (à rendre la plus petite possible) :
  # conflits = pour chaque ligne et chaque colonne, le nombre de chiffres
            # en double, additionnés ensemble.
  # Une grille avec 0 conflit est une solution.


import numpy as np

# Lecture et affichage
def lire_sudoku(chemin_fichier):

   # Lit un fichier généré par qqwing (format « Lisible ») :
     # - les lignes de la grille contiennent des chiffres et des '.' (cases vides),
     #   les '|' servent seulement à séparer les blocs ;
     # - les lignes 'Clé: valeur' (ex. 'Difficulty: Simple') sont les métadonnées.
    #Retourne (grille, fixes, metadonnees).

    valeurs = []
    metadonnees = {}
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()

            # Ligne vide ou ligne de séparation entre les blocs : on la saute
            if not ligne or set(ligne) <= set("-|+"):
                continue

            # Ligne de métadonnées, par exemple "Number of Givens: 24"
            if ":" in ligne:
                cle, valeur = ligne.split(":", 1)
                metadonnees[cle.strip()] = valeur.strip()
                continue

            # Ligne de la grille : on enlève les '|' et on lit chaque case
            for jeton in ligne.replace("|", " ").split():
                valeurs.append(0 if jeton in (".", "0", "_") else int(jeton))

   # Une grille de Sudoku doit avoir exactement 81 cases
    if len(valeurs) != 81:
        raise ValueError(f"{chemin_fichier} : 81 cases attendues, {len(valeurs)} lues")
    grille = np.array(valeurs, dtype=np.int8).reshape(9, 9)
    fixes = grille != 0 # les cases non vides sont celles données par le puzzle
    return grille, fixes, metadonnees


def afficher(grille):
    # Transforme une grille en texte, avec la même présentation que qqwing.
    lignes = []
    for r in range(9):
        if r in (3, 6):
            lignes.append("-------|-------|-------") # séparation entre les bandes de blocs
        cases = ["." if v == 0 else str(v) for v in grille[r]]
        lignes.append(" " + " ".join(cases[0:3]) + " | "
                      + " ".join(cases[3:6]) + " | " + " ".join(cases[6:9]))
    return "\n".join(lignes)


# Création d'une grille de départ.
def cases_libres_par_bloc(fixes):

    # Pour chacun des 9 blocs, donne la liste des cases qu'on a le droit de
    # modifier (celles qui ne sont pas données par le puzzle).
    # Les blocs sont numérotés de 0 à 8, de gauche à droite et de haut en bas.

    blocs = []
    for b in range(9):
        r0, c0 = 3 * (b // 3), 3 * (b % 3) # coin en haut à gauche du bloc b.
        blocs.append([(r, c)
                      for r in range(r0, r0 + 3)
                      for c in range(c0, c0 + 3)
                      if not fixes[r, c]])
    return blocs


def initialiser(grille, fixes, rng):

    # Crée une grille de départ au hasard : dans chaque bloc, on place les
    # chiffres qui manquent dans un ordre aléatoire. Les cases données ne
    # bougent pas. Chaque bloc contient ainsi les chiffres de 1 à 9.

    etat = grille.copy()
    for b in range(9):
        r0, c0 = 3 * (b // 3), 3 * (b % 3)
        bloc = etat[r0:r0 + 3, c0:c0 + 3] # modifier "bloc" modifie aussi "etat".

        # Les chiffres de 1 à 9 qui ne sont pas encore dans le bloc
        manquants = list(set(range(1, 10)) - set(bloc[bloc != 0].tolist()))
        rng.shuffle(manquants)

        # On les place dans les cases libres du bloc
        libres = [(r, c) for r in range(3) for c in range(3) if not fixes[r0 + r, c0 + c]]
        for (r, c), v in zip(libres, manquants):
            bloc[r, c] = v
    return etat

# calcul des conflits.
def conflits(etat):

    # Compte les chiffres en double dans les lignes et les colonnes.
    # Astuce : une fois une ligne triée, deux chiffres identiques se retrouvent
    # côte à côte. Il suffit donc de compter les voisins égaux.

    trie_l = np.sort(etat, axis=1) # chaque ligne triée.
    trie_c = np.sort(etat, axis=0) # chaque colonne triée.
    doublons_lignes = np.count_nonzero(trie_l[:, 1:] == trie_l[:, :-1])
    doublons_colonnes = np.count_nonzero(trie_c[1:, :] == trie_c[:-1, :])
    return int(doublons_lignes + doublons_colonnes)


def conflits_population(population):

    # Même calcul que conflits(), mais pour toute une population de grilles
    # d'un seul coup (tableau de forme (P, 9, 9)). Utilisé par l'algorithme
    # génétique : numpy traite les 200 grilles ensemble, ce qui est bien plus
    # rapide qu'une boucle sur chaque grille.

    trie_l = np.sort(population, axis=2)
    trie_c = np.sort(population, axis=1)
    doublons_lignes = np.count_nonzero(trie_l[:, :, 1:] == trie_l[:, :, :-1], axis=(1, 2))
    doublons_colonnes = np.count_nonzero(trie_c[:, 1:, :] == trie_c[:, :-1, :], axis=(1, 2))
    return doublons_lignes + doublons_colonnes

# Verification finale
def est_solution(etat, grille_initiale):

    # Vérifie qu'une grille est vraiment une solution, sans utiliser la
    # fonction conflits() : chaque ligne, chaque colonne et chaque bloc doit
    # contenir les chiffres de 1 à 9, et les cases données par le puzzle ne
    # doivent pas avoir changé. C'est une double vérification indépendante.

    chiffres = set(range(1, 10))

    # Lignes et colonnes.
    for i in range(9):
        if set(etat[i, :].tolist()) != chiffres or set(etat[:, i].tolist()) != chiffres:
            return False

    # Bloc 3x3.
    for b in range(9):
        r0, c0 = 3 * (b // 3), 3 * (b % 3)
        if set(etat[r0:r0 + 3, c0:c0 + 3].flatten().tolist()) != chiffres:
            return False

    # Les cases données par le puzzle sont restées les memes.
    donnees = grille_initiale != 0
    return bool(np.all(etat[donnees] == grille_initiale[donnees]))