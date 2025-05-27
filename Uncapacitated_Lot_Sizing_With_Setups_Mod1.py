import glob
import time
import csv
import os
import io
import sys
import re
from mip import *

# Prépare la liste des fichiers
files = sorted(glob.glob("Instances_ULS/*Instance*.txt"))

# Fichier pour stocker les résultats
result_file = "resultats_ULS.csv"

# Lire les résultats déjà existants
done_instances = set()
if os.path.exists(result_file):
    with open(result_file, mode="r", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            done_instances.add(row[0])  # instance_name seulement

# Ouvrir le fichier en mode ajout
with open(result_file, mode="a", newline="") as f:
    writer = csv.writer(f)
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


    for datafile in files:
        instance_name = datafile.split("/")[-1]
        if instance_name in done_instances:
            continue  # Déjà traité

    # datafile = "Instances_ULS/Instance21.1.txt"
    # instance_name = datafile.split("/")[-1]
        with open(datafile, "r") as file:
            nbPeriodes = int(file.readline().split()[0])
            demandes = list(map(int, file.readline().split()))
            couts = list(map(int, file.readline().split()))
            cfixes = list(map(int, file.readline().split()))
            cstock = int(file.readline().split()[0])

        results = {}

        for mode in ["normal", "relaxation"]:
            model = Model(name="ULS", solver_name="CBC")
            model.max_seconds = 180

            y = [model.add_var(var_type=BINARY, name=f"y_{i}") for i in range(nbPeriodes)]
            if mode == "normal":
                x = [model.add_var(var_type=INTEGER, name=f"x_{i}") for i in range(nbPeriodes)]
                s = [model.add_var(var_type=INTEGER, name=f"s_{i}") for i in range(nbPeriodes)]
            else:
                x = [model.add_var(var_type=CONTINUOUS, name=f"x_{i}") for i in range(nbPeriodes)]
                s = [model.add_var(var_type=CONTINUOUS, name=f"s_{i}") for i in range(nbPeriodes)]

            model.objective = minimize(
                xsum(couts[i] * x[i] + cfixes[i] * y[i] + cstock * s[i] for i in range(nbPeriodes))
            )

            M = sum(demandes)
            model.add_constr(s[0] == x[0] - demandes[0])
            model.add_constr(demandes[0] <= x[0])
            for i in range(1, nbPeriodes):
                model.add_constr(s[i] == s[i - 1] + x[i] - demandes[i])
                model.add_constr(demandes[i] <= s[i - 1] + x[i])
            for i in range(nbPeriodes):
                model.add_constr(x[i] <= M * y[i])
                model.add_constr(s[i] >= 0)
                model.add_constr(x[i] >= 0)

            start = time.time()
            status = model.optimize()
            duration = time.time() - start

            print(f"\n=== Instance {instance_name}, mode {mode.upper()} terminée ===")
            print("Vérifiez le log CBC ci-dessus et entrez le nombre de nœuds explorés : ", end="")
            try:
                nodes_input = int(sys.stdin.readline().strip())
            except ValueError:
                print("Entrée invalide, j'enregistre None.")
                nodes_input = None



            obj = model.objective_value if model.num_solutions > 0 else None

            results[mode] = {
                "objective": obj,
                "status": status,
                "nodes": nodes_input,
                "time": round(duration, 2)
            }

        obj_n = results["normal"]["objective"]
        obj_r = results["relaxation"]["objective"]

        # Choix de la "meilleure solution" entre normal (entier) et relaxation
        if results["normal"]["status"] == OptimizationStatus.OPTIMAL:
            best_obj = obj_n
            best_status = "OPTIMAL"
        elif results["normal"]["status"] == OptimizationStatus.FEASIBLE:
            best_obj = obj_n
            best_status = "TIME LIMIT, FEASIBLE"
        elif results["relaxation"]["status"] in (OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE):
            best_obj = obj_r
            best_status = "RELAXATION"
        else:
            best_obj = None
            best_status = str(results["normal"]["status"])

        # Calcul de l'écart en %
        if obj_n is not None and obj_r is not None:
            ecart = round(100 * abs(obj_n - obj_r) / obj_n, 2)
        else:
            ecart = None

        # Écriture
        writer.writerow([
            instance_name,
            obj_n,
            obj_r,
            best_status,
            best_obj,
            ecart,
            results["normal"]["nodes"],
            results["relaxation"]["nodes"],
            results["normal"]["time"],
            results["relaxation"]["time"]
        ])
        f.flush()
