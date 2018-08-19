from helpers import *

# x0 = np.array([47,58.5,70,81.5,93,0,1])
# bounds = ((10,100),(10,100),(10,100),(10,100),(10,100),(0,0),(1,1))
# file = "bernwillerfreneC.csv"

x0 = np.array([47,58.5,70,81.5,93,1])
bounds = ((None, None), (None, None), (None, None), (None, None), (None, None), (1,1))
file = "test.csv"
separator = ';'



matrix = converter(file, separator)[1]
results, solution, average_norm, normes, std = computation(matrix, x0, bounds)

print("Results : ", results)

print("Solution : ", solution)
print("Standard deviation : ", std)
print("Average norm : ", average_norm)

#results_refined, solution_refined, average_norm_refined, normes_refined = refine(0.2, results, normes)

#print("Solution : ", solution_refined)
#print("Standard deviation : ", std)
#print("Average norm : ", average_norm_refined)