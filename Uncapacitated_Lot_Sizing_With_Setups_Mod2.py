import glob
import time
import csv
import os
import sys
from mip import *

# Dossier des instances et fichier de résultats
files = sorted(glob.glob("Instances_ULS/*Instance*.txt"))
result_file = "resultats_ULS_xij.csv"

# On saute les instances déjà traitées
done = set()
if os.path.exists(result_file):
    with open(result_file, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            done.add(row[0])

with open(result_file, mode="a", newline="") as f:
    writer = csv.writer(f)
    # Écrire l'en-tête si le fichier est vide
    if os.stat(result_file).st_size == 0:
        writer.writerow([
            "Instance",
            "Solution normale",
            "Solution relaxation",
            "Statut meilleure solution",
            "Meilleure solution",
            "Ecart (%)",
            "Nb noeuds normal",
            "Nb noeuds relaxation",
            "Temps normal (s)",
            "Temps relaxation (s)"
        ])

    # Pour chaque fichier d'instance
    for datafile in files:
        inst = os.path.basename(datafile)
        if inst in done:
            continue

        # Lecture des données
        with open(datafile) as fd:
            n       = int(fd.readline().split()[0])
            demandes= list(map(int, fd.readline().split()))
            couts   = list(map(int, fd.readline().split()))
            cfixes  = list(map(int, fd.readline().split()))
            h       = int(fd.readline().split()[0])

        results = {}

        # Deux modes : entier puis relaxation
        for mode in ["normal", "relaxation"]:
            m = Model(name="ULS_xij", solver_name="CBC")
            m.max_seconds = 180

            # Variables x[i][j] et y[i]
            x = [[
                m.add_var(var_type=(BINARY if mode=="normal" else CONTINUOUS),
                          name=f"x_{i}_{j}")
                for j in range(n)
            ] for i in range(n)]
            y = [m.add_var(var_type=BINARY, name=f"y_{i}") for i in range(n)]

            # Objectif
            m.objective = minimize(
                xsum((couts[i] + h*(j-i)) * demandes[j] * x[i][j]
                     for i in range(n) for j in range(i, n))
                + xsum(cfixes[i] * y[i] for i in range(n))
            )

            # Contraintes
            # 1) Chaque demande j est produite exactement une fois
            for j in range(n):
                m += xsum(x[i][j] for i in range(j+1)) == 1

            # 2) Si on produit à i pour j, y[i] doit être 1
            for i in range(n):
                for j in range(i, n):
                    m += x[i][j] <= y[i]

            # Résolution
            start = time.time()
            status = m.optimize()
            duration = time.time() - start

            # Saisie manuelle du nombre de nœuds
            print(f"\n=== Instance {inst}, mode {mode.upper()} terminé ===")
            print("Entrez le nombre de nœuds explorés par CBC :", end=" ")
            try:
                nodes = int(sys.stdin.readline().strip())
            except ValueError:
                print("Entrée invalide → None")
                nodes = None

            # Récupération de l'objectif
            obj = m.objective_value if m.num_solutions > 0 else None

            results[mode] = {
                "objective": obj,
                "status":     status,
                "nodes":      nodes,
                "time":       round(duration, 2)
            }

        # Calcul du meilleur statut et de l'écart
        obj_n = results["normal"]["objective"]
        obj_r = results["relaxation"]["objective"]
        stat_n = results["normal"]["status"]

        if stat_n == OptimizationStatus.OPTIMAL:
            best_stat, best_obj = "OPTIMAL", obj_n
        elif stat_n == OptimizationStatus.FEASIBLE:
            best_stat, best_obj = "TIME LIMIT, FEASIBLE", obj_n
        elif results["relaxation"]["status"] in (OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE):
            best_stat, best_obj = "RELAXATION", obj_r
        else:
            best_stat, best_obj = str(stat_n), None

        ecart = (round(100 * abs(obj_n - obj_r) / obj_n, 2)
                 if obj_n is not None and obj_r is not None else None)

        # Écriture de la ligne résumée
        writer.writerow([
            inst,
            obj_n,
            obj_r,
            best_stat,
            best_obj,
            ecart,
            results["normal"]["nodes"],
            results["relaxation"]["nodes"],
            results["normal"]["time"],
            results["relaxation"]["time"]
        ])
        f.flush()
