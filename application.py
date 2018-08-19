import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.utils import secure_filename
from cs50 import SQL
import csv

from helpers import *


UPLOAD_FOLDER = '/home/ubuntu/workspace/project/file'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

# Configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def _redirect():
    return render_template("index.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/separator', methods=['GET', 'POST'])
def separator():

    if request.method == 'GET':

        separator = request.args.get("separator")
        saver("file/separator.data", separator)

        response = ['Separator sent']
        return jsonify(response)


@app.route('/', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            error_text = "There is no file in the POST request"
            return redirect("error.html", error_text)

        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            error_text = "Please select a file to upload"
            return redirect("error.html", error_text)

        if file and allowed_file(file.filename):

            # Save the file
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Get the separator
            with open("file/separator.data", 'rb') as f:
                separator = pickle.load(f)

            # Work on the file ie convert it as a matrix
            column_names, matrix = converter(filename, separator)

            # Check if the file has been converted : if an error occured, column_names is the bool False and matrix the error text
            if column_names == False:
                return render_template("error.html", error_text=matrix)
            info_text = "File uploaded"

            # Else, save the file with a normalized name and the data created
            os.rename('file/' + filename, 'file/data.csv')
            saver("file/column_names.data", column_names)
            saver("file/matrix.data", matrix)

            return render_template('parameters.html', info_text=info_text, column_names=column_names, len_column_names=len(column_names))
    error_text = "An unknown error occured. Check the accuracy of the separator"
    return render_template("error.html", error_text=error_text)

@app.route("/parameters", methods=["GET", "POST"])
def parameters():
    """Show the parameters that have to be used and allow the user to choose them"""

    # Get the name of the columns and the matrix
    # Get the separator
    with open("file/separator.data", 'rb') as f:
        separator = pickle.load(f)
    column_names, matrix = converter('data.csv', separator)

    # If parameters are accessed by GET method, use the last data file
    if request.method == 'GET':
        info_text = "The last data file updated has been used"
        return render_template('parameters.html', info_text=info_text, column_names=column_names, len_column_names=len(column_names))

        # Get the list column_names ie the name of the columns, just to know the number of variables

        # With or without bounds ?

    if request.method == 'POST':

        # Get the parameters
        parameters = request.form.to_dict("parameters")

        # Create x0, the initial values, as a list and the bounds as a list of tuples
        x0 = []
        bounds = []
        for i in range(int(len(parameters) / 3)):

            # Get the variables
            lower_bound = "lower_bound_" + str(i + 1)
            value = "value_" + str(i + 1)
            upper_bound = "upper_bound_" + str(i + 1)

            # Add them
            if isfloat(parameters[value]):
                x0.append(float(parameters[value]))

            if isfloat(parameters[lower_bound]) and isfloat(parameters[upper_bound]):
                bounds.append((float(parameters[lower_bound]), float(parameters[upper_bound])))

        # Add the last initial value and bounds as 1 and (1,1) (because of the design of the resolution)
        x0.append(1)
        bounds.append((1,1))

        # Save the initial values
        saver("file/x0.data", x0)
        saver("file/bounds.data", bounds)

        # Solve the problem
        results, solution, average_norm, normes, std = computation(matrix, x0, bounds)

        # Check if a problem occured
        if results == False:
            return render_template("error.html", error_text=solution)

        # Save the solutions
        saver("file/results.data", results)
        saver("file/solution.data", solution)
        #writer("file/average_norm.csv", average_norm)
        saver("file/normes.data", normes)
        saver("file/std.data", std)


        return render_template("results.html", len_results=len(results), len_solution=len(solution), solution=solution, column_names=column_names, std=std, bounds=bounds, x0=x0)

@app.route("/results", methods=["GET", "POST"])
def results():
    """Show the results of the calculation"""

    # Get all the data
    with open("file/results.data", 'rb') as f:
        results = pickle.load(f)
    with open("file/solution.data", 'rb') as f:
        solution = pickle.load(f)
    with open("file/normes.data", 'rb') as f:
        normes = pickle.load(f)
    with open("file/std.data", 'rb') as f:
        std = pickle.load(f)
    with open("file/column_names.data", 'rb') as f:
        column_names = pickle.load(f)
    with open("file/x0.data", 'rb') as f:
        x0 = pickle.load(f)
    with open("file/bounds.data", 'rb') as f:
        bounds = pickle.load(f)

    # Access by GET
    if request.method == 'GET':

        return render_template("results.html", len_results=len(results), column_names=column_names, solution=solution, std=std,
                                len_solution=len(solution), x0=x0, bounds=bounds)

    # User ask to refine the results
    if request.method == 'POST':

        percentage = int(request.form.to_dict("refine")["percentage"]) / 100
        results_refined, solution_refined, average_norm_refined, normes_refined, std_refined = refine(percentage, results, normes)

        return render_template("results.html", len_results=len(results_refined), column_names=column_names, solution=solution_refined, std=std_refined,
                        len_solution=len(solution_refined), x0=x0, bounds=bounds)


@app.route("/parameters_data", methods=["GET", "POST"])
def parameters_data():

    if request.method == 'GET':
        with open("file/x0.data", 'rb') as f:
            x0 = pickle.load(f)
        with open("file/bounds.data", 'rb') as f:
            bounds = pickle.load(f)

        return jsonify([x0, bounds])