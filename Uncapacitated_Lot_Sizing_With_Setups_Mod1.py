

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

status = model.optimize()

print("\n----------------------------------")
if status == OptimizationStatus.OPTIMAL:
    print("Status de la résolution: OPTIMAL")
elif status == OptimizationStatus.FEASIBLE:
    print("Status de la résolution: TEMPS LIMITE et SOLUTION REALISABLE CALCULEE")
elif status == OptimizationStatus.NO_SOLUTION_FOUND:
    print("Status de la résolution: TEMPS LIMITE et AUCUNE SOLUTION CALCULEE")
elif status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.INT_INFEASIBLE:
    print("Status de la résolution: IRREALISABLE")
elif status == OptimizationStatus.UNBOUNDED:
    print("Status de la résolution: NON BORNE")
    
if model.num_solutions>0:
    print("Solution calculée")
    print("-> Valeur de la fonction objectif de la solution calculée : ",  model.objective_value)
    for i in range(nbPeriodes):
        print("\t",i, " : ", x[i].x, " unités produites")
        print("\t",i, " : ", s[i].x, " unités en stock")
        print("\t",i, " : ", y[i].x, " production lancée")
        print("\t",i, " : ", demandes[i], " unités demandées")
        print("")

    print("\n \t Implémentez l'affichage de la solution !")

