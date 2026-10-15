# main.py - Programme principal de la partie 2 (Sudoku)

# Ce fichier lance le hill climbing et l'algorithme génétique sur chaque puzzle
# du dossier Entree, 10 fois chacun, et enregistre les résultats.

# Comment le lancer (depuis le dossier Partie2_sudoku) :
   # python main.py                 # les deux algorithmes sur tous les puzzles
   # python main.py hc              # seulement le hill climbing
   # python main.py ag              # seulement l'algorithme génétique
   # python main.py ag Entree/sudoku01_Simple.txt   # un algorithme, un seul puzzle

# Pour chaque puzzle, chaque algorithme et chaque exécution, on crée un fichier
# Resultats/<ALGO>_<puzzle>_execNN.txt (même format que le laboratoire 1) :
 #  - une ligne par itération (valeurs séparées par des tabulations)
   #   HC : itération <TAB> conflits courants <TAB> redémarrages
    #  AG : génération <TAB> meilleurs conflits <TAB> conflits moyens <TAB> redémarrages
 # - avant-dernière ligne : nombre total d'itérations
  # - dernière ligne : temps d'exécution (s)

# La grille obtenue à chaque exécution (la solution, ou la meilleure grille
# trouvée en cas d'échec) est aussi enregistrée dans le dossier Solutions.

# L'exécution numéro i utilise toujours la même suite de nombres aléatoires
# (graine i) : si on relance le programme, on retrouve les mêmes itérations.

import os
import sys
import glob

import numpy as np

from sudoku import lire_sudoku, afficher, est_solution
from hill_climbing import hill_climbing
from genetique import genetique

NB_EXECUTIONS = 10 # nombre d'exécutions par puzzle et par algorithme

# Les chemins des dossiers sont construits à partir de l'emplacement de main.py,
# pour que le programme fonctionne peu importe d'où on le lance.
DOSSIER_BASE = os.path.dirname(os.path.abspath(__file__))
DOSSIER_ENTREE = os.path.join(DOSSIER_BASE, "Entree")
DOSSIER_RESULTATS = os.path.join(DOSSIER_BASE, "Resultats")
DOSSIER_SOLUTIONS = os.path.join(DOSSIER_BASE, "Solutions")

# Les deux algorithmes testés, avec le nom court utilisé dans les fichiers.
ALGORITHMES = {
    "HC": hill_climbing,
    "AG": genetique,
}

# Ecrire des fichiers.
def ecrire_resultats(algo, nom_puzzle, num_exec, resultat):
    os.makedirs(DOSSIER_RESULTATS, exist_ok=True) # permet de créer le dossier s'il n'existe pas
    chemin = os.path.join(DOSSIER_RESULTATS, f"{algo}_{nom_puzzle}_exec{num_exec:02d}.txt")
    with open(chemin, "w", encoding="utf-8") as f:
        for ligne in resultat["trace"]:
            # Les nombres à virgule (conflits moyens du génétique) sont écrits avec 2 décimales.
            f.write("\t".join(f"{x:.2f}" if isinstance(x, float) else str(x) for x in ligne) + "\n")
        f.write(f"{resultat['iterations']}\n")    # avant-dernière ligne
        f.write(f"{resultat['temps']:.6f}\n")     # dernière ligne


def ecrire_solution(algo, nom_puzzle, num_exec, resultat):
    # Écrit la grille obtenue, précédée de SOLUTION ou ECHEC.
    os.makedirs(DOSSIER_SOLUTIONS, exist_ok=True)
    chemin = os.path.join(DOSSIER_SOLUTIONS, f"{algo}_{nom_puzzle}_exec{num_exec:02d}.txt")
    with open(chemin, "w", encoding="utf-8") as f:
        statut = "SOLUTION" if resultat["trouve"] else f"ECHEC ({resultat['meilleur_cout']} conflits)"
        f.write(statut + "\n\n")
        f.write(afficher(resultat["etat"]) + "\n")

# Traitement d'un puzzle.
def traiter(fichier, algos):
    nom_puzzle = os.path.splitext(os.path.basename(fichier))[0]
    grille, fixes, meta = lire_sudoku(fichier)
    difficulte = meta.get("Difficulty", "?") # difficulté indiquée par qqwing
    print(f"===== {nom_puzzle} ({difficulte}, {int(fixes.sum())} cases donnees) =====")
    print(afficher(grille) + "\n")

    resume = []
    for algo in algos:
        fonction = ALGORITHMES[algo]
        temps, iterations, succes = [], [], 0
        for i in range(1, NB_EXECUTIONS + 1):
            # La graine i rend l'exécution reproductible
            resultat = fonction(grille, fixes, np.random.default_rng(i))
            if resultat["trouve"]:

                # Double vérification : on contrôle la solution avec une fonction
                # indépendante du calcul des conflits.
                assert est_solution(resultat["etat"], grille), "solution invalide !"
                succes += 1
            temps.append(resultat["temps"])
            iterations.append(resultat["iterations"])
            ecrire_resultats(algo, nom_puzzle, i, resultat)
            ecrire_solution(algo, nom_puzzle, i, resultat)
            statut = "resolu" if resultat["trouve"] else f"echec ({resultat['meilleur_cout']} conflits)"
            print(f"  {algo} exec {i:2d}/{NB_EXECUTIONS} : {resultat['iterations']:6d} iterations | "
                  f"{resultat['redemarrages']:4d} redemarrages | {resultat['temps']:7.3f} s | {statut}")

            # moyenne des 10 exécutions.
        t_moy, it_moy = float(np.mean(temps)), float(np.mean(iterations))
        print(f"  -> {algo} : {succes}/{NB_EXECUTIONS} resolus, {it_moy:.0f} iterations "
              f"et {t_moy:.3f} s en moyenne\n")
        resume.append((nom_puzzle, difficulte, algo, succes, it_moy, t_moy))
    return resume

# Programme principal:
def main():
    args = sys.argv[1:]
    # Premier argument facultatif : « hc » ou « ag » pour un seul algorithme
    algos = list(ALGORITHMES)
    if args and args[0].upper() in ALGORITHMES:
        algos = [args[0].upper()]
        args = args[1:]

    # Arguments suivants facultatifs : les puzzles à traiter (sinon tout le dossier Entree)
    fichiers = args or sorted(glob.glob(os.path.join(DOSSIER_ENTREE, "*.txt")))
    if not fichiers:
        print(f"Aucun fichier trouve dans {DOSSIER_ENTREE}")
        return

    resume = []
    for fichier in fichiers:
        resume.extend(traiter(fichier, algos))

# ce bout de code nous affiche le tableau récapitulatif à la fin
    print(f"===== RESUME ({NB_EXECUTIONS} executions par puzzle) =====")
    print(f"{'Puzzle':<28}{'Difficulte':<14}{'Algo':<6}{'Resolus':>9}{'Iter. moy.':>12}{'Temps moy. (s)':>16}")
    for p, d, a, s, it, t in resume:
        print(f"{p:<28}{d:<14}{a:<6}{f'{s}/{NB_EXECUTIONS}':>9}{it:>12.0f}{t:>16.3f}")


if __name__ == "__main__":
    main()