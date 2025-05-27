import glob
import time
import csv
import os
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
        next(reader)  # Skip header
        for row in reader:
            done_instances.add((row[0], row[1]))  # (filename, mode)

# Ouvrir le fichier en mode ajout
with open(result_file, mode="a", newline="") as f:
    writer = csv.writer(f)
    if os.stat(result_file).st_size == 0:
        writer.writerow(["Instance", "Mode", "Status", "Time(s)", "Nodes", "Objective"])

    for datafile in files:
        with open(datafile, "r") as file:
            nbPeriodes = int(file.readline().split()[0])
            demandes = list(map(int, file.readline().split()))
            couts = list(map(int, file.readline().split()))
            cfixes = list(map(int, file.readline().split()))
            cstock = int(file.readline().split()[0])

        for mode in ["normal", "relaxation"]:
            instance_name = datafile.split("/")[-1]
            if (instance_name, mode) in done_instances:
                continue  # Déjà traité

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

            status_str = {
                OptimizationStatus.OPTIMAL: "OPTIMAL",
                OptimizationStatus.FEASIBLE: "TIME LIMIT, FEASIBLE",
                OptimizationStatus.NO_SOLUTION_FOUND: "TIME LIMIT, NO SOLUTION",
                OptimizationStatus.INFEASIBLE: "INFEASIBLE",
                OptimizationStatus.INT_INFEASIBLE: "INFEASIBLE",
                OptimizationStatus.UNBOUNDED: "UNBOUNDED",
            }.get(status, str(status))

            try:
                nodes = model.num_nodes
            except AttributeError:
                nodes = None

            obj = model.objective_value if model.num_solutions > 0 else None

            writer.writerow([
                instance_name, mode, status_str, round(duration, 2), nodes, obj
            ])
            f.flush()  # Pour être sûr que le fichier est mis à jour immédiatement
