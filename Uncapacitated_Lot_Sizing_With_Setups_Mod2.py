
datafileName = 'Instances_USILS/Instance120.1.txt'

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


model2 = Model(name = "ULS", solver_name="CBC")

y = 
x = 






#model2.write("test.lp")

status = model2.optimize()

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
    
if model2.num_solutions>0:
    print("Solution calculée")
    print("-> Valeur de la fonction objectif de la solution calculée : ",  model2.objective_value)

    print("\n \t Implémentez l'affichage de la solution !")

