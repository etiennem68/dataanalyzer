import pickle
import pygal
import numpy as np
import scipy as sc
from scipy import optimize, special
from itertools import combinations as cb
import time

# Save a data file
def saver(path, list_to_save):
    with open(path,'wb') as resultFile:
        pickle.dump(list_to_save, resultFile)
    return True


# Check if a string is a float (ie contains digit and '.')
def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# Check the viability of the file and change it in consequence
def check_data(matrix):

    column_names = []

    # Check if the first row is names
    for column, string in enumerate(matrix[0]):

        # If so, stock them in a new row independant of the matrix
        if not isfloat(string):
            column_names = matrix[0]
            matrix = matrix[1:]

            # Need to exit the loop
            break
        # If there is numbers, convert them
        else:
            column_names.append('Value ' + str(column + 1))
            matrix[0][column] = float(string)

    # Change every remaining numbers from string to float, if it's possible
    for line, row in enumerate(matrix):
        for column, string in enumerate(row):
            if isfloat(string):
                matrix[line][column] = float(string)

            # Return error message if the data is incorrect
            else:
                print('Some data are not numbers')
                error_text = "Some data in the file are not numbers. Check if the separator you have choosen is the one used in the file"
                return False, error_text

    # Return the list of names and the matrix with numbers
    return column_names, matrix


# Transform the file in a single matrix
def converter(filename, separator):

    # Check if the separator is a correct string (should implement a list of supported separators)
    separators = [';', ' ', ',', """\\t"""]
    if separator not in separators:
        print('False separator : ', separator)
        error_text = "False separator. Please use a separator in the list"
        return False, error_text
    if separator == "\\t":
        separator = '\t'


    # Open the csv file
    file = "file/" + filename
    rows = open(file, "r")
    if not rows:
        print('Unable to open file')
        error_text = "Unable to open file"
        return False, error_text

    # Get all the rows (ie the lines)
    matrix = []
    for counter, row in enumerate(rows):

        matrix.append(row.split(separator))

        # Change the ',' as '.' if needed
        for i, string in enumerate(matrix[counter]):
            matrix[counter][i] = string.replace(",",".")

        # Delete the \n at the end of each file
        matrix[counter][-1] = matrix[counter][-1].rstrip("\n")

    # Check the data and convert it to float
    #print(matrix)
    column_names, matrix = check_data(matrix)

    # An error occured
    if column_names == False:
        return column_names, matrix

    # Multiply the last elements (ie the price) by -1, so we get A*X = 0
    for line, row in enumerate(matrix):
        matrix[line][-1] = (-1) * row[-1]

    return column_names, matrix

# Extract every possible square matrix
def combinations_calculator(matrix):
    """ Give a number (ie a name) to each row of matrix
        Search all the possible combinations of rows and save that in list of names (ie list of numbers)
        Create each different matrix only once in the resolution function to save space"""

    # Give a name to each row of the matrix
    names = []
    for i in range(len(matrix)):
        names.append(i)

    # Search all the possible combinations
    combinations = list(cb(names, len(matrix[0])))

    # If the matrix is square (ie n lines, n+1 columns with the solution column), combination = []
    if combinations == []:

        t = ()
        for i in range(len(matrix)):
            t += (i,)
        combinations.append(t)

        return combinations

    # Return a list of every combinations
    return combinations

# Resolve the equation for a matrix by using initial conditions and boundaries
def resolution(matrix, x0, bounds):

    """ We use an optimization algorithm
        We have a matrix called let's say A and we search a vector X following 0 - epsilon < A*X < 0 + epsilon
        We want epsilon (an Rn vector) to be as small as possible, but with (x1,..., xn) in the bounds (if requested)
        To make the comparison easier, we will use the norm : || A*X || < 0 + epsilon, epsilon in R
    """

    # Create a function as required and
    try:
        f = lambda x: np.linalg.norm(np.dot(matrix,x))
    except ValueError:
        error_text = "Unable to create the norm function. Dimension error, check the file and the parameters"
        return [False, error_text, None]

    # Solve the optimization
    result = sc.optimize.minimize(f, x0, method='SLSQP', bounds=bounds)

    # Get the attributes
    solution = result.x
    success = result.success # Is a boolean

    # Get the norm
    norm = np.linalg.norm(np.dot(matrix, solution))

    return [solution, success, norm]


# Analyse the whole data
def computation(matrix, x0, bounds):


    # Get the combinations
    combinations = combinations_calculator(matrix)

    # Iterate through the different matrixes
    results = []
    matrix = np.array(matrix)
    for combination in combinations:
        extracted_matrix = matrix[list(combination)]

        # Solve the optimization for each square matrix and store it
        result = resolution(extracted_matrix, x0, bounds)

        try:
            if result[0] == False:
                return False, result[1], None, None, None
        except ValueError:
            results.append(result)


    # Provide analysis
    solutions = []
    for result in results:
        solutions.append(result[0])

    solution = np.mean(solutions, axis=0)
    std = np.std(solutions, axis=0)

    # Sort the normes
    normes = []
    for result in results:
        normes.append(result[2])
    normes.sort()
    average_norm = np.mean(normes, axis=0)

    # results is a list containing every solution, success and norm of every matrix
    # solution is a list of the solution of each variable, as an average
    return results, solution, average_norm, normes, std

# Refine and select
def refine(percentage, results, normes):
    """ Allow the user to perform the analysis on a certain percentage of the results
        If the user request 10%, the first 10% of the results (ie the solutions) will be used for the average solution
        The results will be sorted from the best (ie low norm) to the worst (ie high norm)
        """
    results_refined = []
    limit = normes[int(len(normes) * percentage)]

    #print(limit)

    for result in results:
        if result[2] <= limit:
            results_refined.append(result)

    # Provide analysis
    solutions_refined = []
    for result in results_refined:
        solutions_refined.append(result[0])

    solution_refined = np.mean(solutions_refined, axis=0)
    std_refined = np.std(solutions_refined, axis=0)


    # Sort the normes
    normes_refined = []
    for result in results_refined:
        normes_refined.append(result[2])
    normes_refined.sort()
    average_norm_refined = np.mean(normes_refined, axis=0)

    #print(solution_refined)
    #print(std_refined)

    return results_refined, solution_refined, average_norm_refined, normes_refined, std_refined