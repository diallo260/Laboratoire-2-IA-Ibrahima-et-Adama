# puzzle.py - Représentation du 8-puzzle

# Ce fichier contient tout ce qui concerne le jeu lui-même :
# lire un puzzle dans un fichier, l'afficher, trouver les déplacements
# possibles et vérifier si le puzzle a une solution.

# Un état du puzzle est un tuple de 9 nombres, lus ligne par ligne.
# La case vide est représentée par 0.
# Exemple :   7 2 4
           #  5 _ 6   -->  (7, 2, 4, 5, 0, 6, 8, 3, 1)
           #  8 3 1

# On utilise un tuple (et non une liste) parce qu'un tuple ne peut pas être
# modifié : Python peut donc s'en servir comme clé dans un dictionnaire ou un
# ensemble. A* en a besoin pour retenir rapidement les états déjà visités.

# L'etat que l'on cherche à atteindre : les tuiles dans l'ordre, case vide à la fin.
ETAT_OBJECTIF = (1, 2, 3,
                 4, 5, 6,
                 7, 8, 0)

# Les 4 déplacements possibles de la case vide :
# (nom du mouvement, changement de ligne, changement de colonne)
MOUVEMENTS = [
    ("haut", -1, 0),
    ("bas", 1, 0),
    ("gauche", 0, -1),
    ("droite", 0, 1),
]


def lire_puzzle(chemin_fichier):

    # Lit un fichier 3x3. Format du labo 1 : valeurs séparées par des
    # tabulations, case vide = cellule vide. Accepte aussi '_' ou '0'.

    valeurs = []
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.rstrip("\r\n")
            if not ligne.strip():
                continue  # ignore les lignes vides

            # Avec des tabulations, une case vide donne un texte vide entre deux
            # tabulations. On découpe donc sur les tabulations pour ne pas la perdre.
            jetons = ligne.split("\t") if "\t" in ligne else ligne.split()
            for jeton in jetons:
                jeton = jeton.strip()
                valeurs.append(0 if jeton in ("", "_", "0") else int(jeton))

    # un puzzle valide contient exactement les nombres de 0 à 8, chacun une fois.
    if len(valeurs) != 9 or sorted(valeurs) != list(range(9)):
        raise ValueError(f"Puzzle invalide dans {chemin_fichier} : {valeurs}")
    return tuple(valeurs)


def afficher(etat):
    # Transforme un état en petite grille 3x3 facile à lire (case vide = '_')."""
    lignes = []
    for i in range(3):
        cases = etat[3 * i: 3 * i + 3] # les 3 cases de la ligne i.
        lignes.append(" ".join("_" if v == 0 else str(v) for v in cases))
    return "\n".join(lignes)


def successeurs(etat):

    # Fonction successeur S(x) vue en cours.
    # Retourne la liste des états que l'on peut atteindre en un seul coup,
    # sous la forme (nom du mouvement, nouvel état). Chaque coup coûte 1.

    resultat = []

    # On repère la position de la case vide dans la grille.
    pos_vide = etat.index(0)
    ligne, col = divmod(pos_vide, 3) # convertit la position  0 à 8 en ligne, colonne.
    for nom, dl, dc in MOUVEMENTS:
        nl, nc = ligne + dl, col + dc

    # Le mouvement n'est possible que si la case vide reste dans la grille.
        if 0 <= nl < 3 and 0 <= nc < 3:
            nouvelle_pos = 3 * nl + nc
    # On échange la case vide avec la tuile voisine
            liste = list(etat)
            liste[pos_vide], liste[nouvelle_pos] = liste[nouvelle_pos], liste[pos_vide]
            resultat.append((nom, tuple(liste)))
    return resultat


def est_soluble(etat):
    # Vérifie si le puzzle a une solution.
    # On compte les « inversions » : les paires de tuiles qui apparaissent dans
    # le mauvais ordre quand on lit la grille ligne par ligne (sans la case vide).
    # Pour un 8-puzzle, il existe une solution seulement si ce nombre est pair.
    # Cela permet de reconnaître tout de suite un puzzle impossible comme Ex1-3.

    tuiles = [v for v in etat if v != 0]
    inversions = sum(
        1
        for i in range(len(tuiles))
        for j in range(i + 1, len(tuiles))
        if tuiles[i] > tuiles[j]
    )
    return inversions % 2 == 0