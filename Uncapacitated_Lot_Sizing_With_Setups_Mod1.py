

datafileName = 'Instances_ULS/Instance60.1.txt'

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




from mip import *
import time

model = Model(name = "ULS", solver_name="CBC")

#POUR AVOIR RELAXATION X PASSE DE INTEGER A CONTINUOUS

y = [model.add_var(name="y_" + str(i), var_type=BINARY) for i in range(nbPeriodes)]
x = [model.add_var(name="x_" + str(i), var_type=CONTINUOUS) for i in range(nbPeriodes)]
s = [model.add_var(name="s_" + str(i), var_type=CONTINUOUS) for i in range(nbPeriodes)]


model.objective = minimize(xsum(couts[i]*x[i] + cfixes[i]*y[i] + cstock*s[i] for i in range(nbPeriodes)))
model.max_seconds = 180

M = sum(demandes)
# période 0
model.add_constr(s[0] == x[0] - demandes[0])
model.add_constr(demandes[0] <= x[0])

# périodes i>0
for i in range(1, nbPeriodes):
    model.add_constr(s[i] == s[i-1] + x[i] - demandes[i])
    model.add_constr(demandes[i] <= s[i-1] + x[i])


for i in range(nbPeriodes):
    model.add_constr(x[i] <= M*y[i])
    model.add_constr(s[i] >= 0)
    model.add_constr(x[i] >= 0)

#model.write("test.lp")

# Mesure du temps
start_time = time.time()
status = model.optimize()
end_time = time.time()

print("\n" + "-"*50)
# 1) Statut
if status == OptimizationStatus.OPTIMAL:
    print("Status de la résolution : OPTIMAL")
elif status == OptimizationStatus.FEASIBLE:
    print("Status de la résolution : TEMPS LIMITE et SOLUTION RÉALISABLE CALCULÉE")
elif status == OptimizationStatus.NO_SOLUTION_FOUND:
    print("Status de la résolution : TEMPS LIMITE et AUCUNE SOLUTION CALCULÉE")
elif status in (OptimizationStatus.INFEASIBLE, OptimizationStatus.INT_INFEASIBLE):
    print("Status de la résolution : IRRÉALISABLE")
elif status == OptimizationStatus.UNBOUNDED:
    print("Status de la résolution : NON BORNÉ")
else:
    print(f"Status de la résolution : {status}")

print(f"Temps d'exécution        : {end_time - start_time:.2f} s")

# 3) Solution détaillée
# if model.num_solutions > 0:
#     print("\nSolution calculée :")
#     print("→ Valeur de la fct objectif :", model.objective_value)
#     for i in range(nbPeriodes):
#         print(f"\tPériode {i} : production = {x[i].x:.0f}, "
#               f"stock = {s[i].x:.0f}, lancement = {y[i].x:.0f}, "
#               f"demandes = {demandes[i]}")
# else:
#     print("\nAucune solution disponible.")

print("-"*50)
