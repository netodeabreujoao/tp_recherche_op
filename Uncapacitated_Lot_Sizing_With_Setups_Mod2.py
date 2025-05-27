from mip import *
import glob
import time
import csv
import os

files = sorted(glob.glob("Instances_ULS/*Instance*.txt"))
result_file = "resultats_ULS_xij.csv"

done_instances = set()
if os.path.exists(result_file):
    with open(result_file, mode="r", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            done_instances.add((row[0], row[1]))

with open(result_file, mode="a", newline="") as f:
    writer = csv.writer(f)
    if os.stat(result_file).st_size == 0:
        writer.writerow(["Instance", "Mode", "Status", "Time(s)", "Nodes", "Objective"])


    for datafileName in files:

        with open(datafileName, "r") as file:
            line = file.readline()  
            lineTab = line.split()    
            nbPeriodes = int(lineTab[0])
            
            line = file.readline()  
            lineTab = line.split()
            demandes = []
            for i in range(nbPeriodes):
                demandes.append(int(lineTab[i]))
                
            line = file.readline()  
            lineTab = line.split()
            couts = []
            for i in range(nbPeriodes):
                couts.append(int(lineTab[i]))

            line = file.readline()  
            lineTab = line.split()
            cfixes = []
            for i in range(nbPeriodes):
                cfixes.append(int(lineTab[i]))
            
            line = file.readline()  
            lineTab = line.split()    
            cstock = int(lineTab[0])

        #print(nbPeriodes)
        #print(demandes)
        #print(couts)
        #print(cfixes)
        #print(cstock)


        for mode in ["normal", "relaxation"]:
            instance_name = datafile.split("/")[-1]
            if (instance_name, mode) in done_instances:
                continue

            model = Model(name="ULS_xij", solver_name="CBC")
            model.max_seconds = 180

            x = [[model.add_var(var_type=(BINARY if mode == "normal" else CONTINUOUS), name=f"x_{i}_{j}")
                  for j in range(nb)] for i in range(nb)]
            y = [model.add_var(var_type=BINARY, name=f"y_{i}") for i in range(nb)]

            # Objectif
            model.objective = minimize(
                xsum(
                    (c[i] + h * (j - i)) * d[j] * x[i][j]
                    for i in range(nb) for j in range(i, nb)
                ) + xsum(f_costs[i] * y[i] for i in range(nb))
            )

            # Contraintes
            for j in range(nb):
                model += xsum(x[i][j] for i in range(j + 1)) == 1  # chaque demande est satisfaite exactement une fois

            for i in range(nb):
                for j in range(i, nb):
                    model += x[i][j] <= y[i]  # si on produit pour j à i, alors y_i = 1

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
            f.flush()
