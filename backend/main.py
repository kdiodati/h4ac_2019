#!/usr/bin/env python3
'''
main.py

Core Flask logic for the Homeless Resource Finder application

Hack for a Cause 2019

Team: dont-spoil-endgame
'''

# Python libraries
import json, os, operator, datetime
from flask import Flask, request, redirect, url_for, flash, abort, jsonify, render_template, session
import flask
from pymongo import MongoClient

# Establish flask application on startup
app = flask.Flask(__name__, static_folder="../static", template_folder="../templates")

# Establish database at run time
# Get the MongoDB client
client = MongoClient('mongodb://dontspoilendgame:thanos123@cluster0-shard-00-00-spqqu.mongodb.net:27017,cluster0-shard-00-01-spqqu.mongodb.net:27017,cluster0-shard-00-02-spqqu.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true')

# Get the MongoDB database we are using
db = client.homelessData

# Get the MongoDB database collection we are using to present information from
data = db.test
# Get the MongoDB database collection we are using to collect user information
data_out = db.test_out

class CreateDictionary:
    """
    A class that creates a dictionary with set keys initialized to None. Provides an easy and streamlined way to create a
    dictionary that is in the correct format to be used to search in the MongoDB database.
    """
    def __init__(self, gender=None, age=None, veteran=None, disabled=None, pets=None, family=None, food=None, beds=None, clinic=None):
        # Assign all arguments to their own class variable
        self.gender = gender
        self.age = age
        self.veteran = veteran
        self.disabled = disabled
        self.pets = pets
        self.family = family
        self.food = food
        self.beds = beds
        self.clinic = clinic
        # Create a dictionary with all of the aforementioned variables
        self.current_dict = {"Gender": self.gender, "Age": self.age, "Veteran": self.veteran, "Disabled": self.disabled, "Pets": self.pets, "Family": self.family, "Food": self.food, "Beds": self.beds, "Clinic": self.clinic}

    def __repr__(self):
        # Cleanly print the dictionary
        return '{}'.format(self.current_dict)

    def update_dictionary(self):
        # Update the dictionary in order to get rid of None values and keys from the webpage
        for k, v in list(self.current_dict.items()):
            if v == None:
                del self.current_dict[k]

    def add_val(self, key, value):
        # Add a key and value to the dictionary
        self.current_dict[key] = value

    def get_dictionary(self):
        # Return the dictionary in the format to search the database
        return self.current_dict

@app.route("/")
@app.route("/about", methods=['POST', 'GET'])
def aboutForm():
    # Render the template for the home page when the user first goes to the site
    return flask.render_template("about.html")

@app.route("/about_es", methods=['POST', 'GET'])
def about_es():
    return flask.render_template("about_es.html")

@app.route("/index", methods=['POST', 'GET'])
def index():
    """
    The default page which is an initial filter page that allows the client to send various amounts of information
    to the server in order to check whether or not the requested resource is in the database. Redirects to
    the results page with the specified parameters.
    """
    print("entering aboutForm")
    # Request the information from the webpage based on what the user entered/selected
    gender = flask.request.form.get("gender")
    age = flask.request.form.get("age")
    veteran = flask.request.form.get("veteran")
    disabled = flask.request.form.get("disabled")
    pets = flask.request.form.get("pets")
    family = flask.request.form.get("family")
    # Create a dictionary object for use in matching it to a database document
    diction = CreateDictionary(gender, age, veteran, disabled, pets, family)
    # Save the new dictionary in its own session variable for easier access
    flask.session["current_dict"] = diction.get_dictionary()
    # Render the next page's template
    return flask.render_template("index.html")

@app.route("/index_es", methods=['POST', 'GET'])
def index_es():
    """
    The default page which is an initial filter page that allows the client to send various amounts of information
    to the server in order to check whether or not the requested resource is in the database. Redirects to
    the results page with the specified parameters.
    """
    print("entering aboutForm")
    # Request the information from the webpage based on what the user entered/selected
    gender = flask.request.form.get("gender")
    age = flask.request.form.get("age")
    veteran = flask.request.form.get("veteran")
    disabled = flask.request.form.get("disabled")
    pets = flask.request.form.get("pets")
    family = flask.request.form.get("family")
    # Create a dictionary object for use in matching it to a database document
    diction = CreateDictionary(gender, age, veteran, disabled, pets, family)
    # Save the new dictionary in its own session variable for easier access
    flask.session["current_dict"] = diction.get_dictionary()
    # Render the next page's template
    return flask.render_template("index_es.html")

def formatBed(my_list):
    '''
    Formats the list into a usable form for the HTML
    '''
    # Create global jinja values for use in the HTML later
    flask.g.results = []
    flask.g.empty = False

    count = 0
    # Loop through the given list
    for i in my_list:
        # Add a list of restrictions that users can flock to
        flask.g.results.append({"Restrictions":[]})
        # Pre-assign the Name value to an empty string for easier parsing and manipulation
        flask.g.results[count]['Name'] = ""
        # If the entry is in the dictionary and the restriction is active for that service: append the image file name
        if ("Gender" in i and i['Gender'] == "F"):
            flask.g.results[count]['Restrictions'].append('female.png')
        if ("Veteran" in i and i['Veteran'] == "Y"):
            flask.g.results[count]['Restrictions'].append('veteran.png')
        if ("Disabled" in i and i['Disabled'] == "Y"):
            flask.g.results[count]['Restrictions'].append('disabled.png')
        # Keep up-to-date info on available beds and attach it to Name for ease of use
        if ("Beds" in i and i['Beds'] != "N"):
            flask.g.results[count]['Name'] = str(i['Beds'] + " beds open at ")
        else:
            # If there aren't any beds, delete the key and entry. Since we're in the format function for beds
            # it's assumed that the service has beds, so since it doesn't, there's no point displaying it.
            del flask.g.results[count]
            continue
        # If the dictionary has a name: check if it's too long
        if ("Name" in i):
            # If it is, add an ellipse to the end
            if (len(i["Name"]) > 36):
                flask.g.results[count]['Name'] += str(i["Name"][:36] + "...")
            # If not, then keep the name as it is (Already have part of a string in this value so we can +=)
            elif (len(i["Name"]) > 0 and flask.g.results[count]['Name'] != ""):
                flask.g.results[count]['Name'] += str(i["Name"])
            # None of the string is formed yet, so we have to create a new one
            else:
                # Put a name into results for display on the site
                flask.g.results[count]['Name'] = str(i["Name"])
        # If these values are sent in correctly, put them in the flask g results
        if ("Address" in i and i['Address'] != None):
            flask.g.results[count]['Address'] = i["Address"]
        if ("Phone" in i and i['Phone'] != None):
            flask.g.results[count]['Phone'] = i["Phone"]
        if ("EndpointName" in i and i['EndpointName'] != None):
            flask.g.results[count]['EndpointName'] = i["EndpointName"]
        #Check if there are any reservations on who can use this clinic
        if len(flask.g.results[count]["Restrictions"]) == 0:
            flask.g.results[count]["Restrictions"].append(True)
        count += 1
    # Handle bad case
    if len(flask.g.results) == 0:
        flask.g.empty = True

def formatBedEs(my_list):
    '''
    Formats the list into a usable form for the HTML
    '''
    # Create global jinja values for use in the HTML later
    flask.g.results = []
    flask.g.empty = False

    count = 0
    # Loop through the given list
    for i in my_list:
        # Add a list of restrictions that users can flock to
        flask.g.results.append({"Restrictions":[]})
        # Pre-assign the Name value to an empty string for easier parsing and manipulation
        flask.g.results[count]['Name'] = ""
        # If the entry is in the dictionary and the restriction is active for that service: append the image file name
        if ("Gender" in i and i['Gender'] == "F"):
            flask.g.results[count]['Restrictions'].append('female.png')
        if ("Veteran" in i and i['Veteran'] == "Y"):
            flask.g.results[count]['Restrictions'].append('veteran.png')
        if ("Disabled" in i and i['Disabled'] == "Y"):
            flask.g.results[count]['Restrictions'].append('disabled.png')
        # Keep up-to-date info on available beds and attach it to Name for ease of use
        if ("Beds" in i and i['Beds'] != "N"):
            flask.g.results[count]['Name'] = str(str(i['Beds']) + " camas abiertas en ")
        else:
            # If there aren't any beds, delete the key and entry. Since we're in the format function for beds
            # it's assumed that the service has beds, so since it doesn't, there's no point displaying it.
            del flask.g.results[count]
            continue
        # If the dictionary has a name: check if it's too long
        if ("Name" in i):
            # If it is, add an ellipse to the end
            if (len(i["Name"]) > 36):
                flask.g.results[count]['Name'] += str(i["Name"][:36] + "...")
            # If not, then keep the name as it is (Already have part of a string in this value so we can +=)
            elif (len(i["Name"]) > 0 and flask.g.results[count]['Name'] != ""):
                flask.g.results[count]['Name'] += str(i["Name"])
            # None of the string is formed yet, so we have to create a new one
            else:
                # Put a name into results for display on the site
                flask.g.results[count]['Name'] = str(i["Name"])
        # If these values are sent in correctly, put them in the flask g results
        if ("Address" in i and i['Address'] != None):
            flask.g.results[count]['Address'] = i["Address"]
        if ("Phone" in i and i['Phone'] != None):
            flask.g.results[count]['Phone'] = i["Phone"]
        if ("EndpointName" in i and i['EndpointName'] != None):
            flask.g.results[count]['EndpointName'] = i["EndpointName"]
        #Check if there are any reservations on who can use this clinic
        if len(flask.g.results[count]["Restrictions"]) == 0:
            flask.g.results[count]["Restrictions"].append(True)
        count += 1
    # Handle bad case
    if len(flask.g.results) == 0:
        flask.g.empty = True


def formatFood(my_list):
    """
    Same as the formatBed function, except it handles food.
    """
    flask.g.results = []
    flask.g.empty = False
    count = 0
    for i in my_list:
        flask.g.results.append({"Restrictions":[]})
        # Pre-assign the Name value to an empty string for easier parsing and manipulation
        flask.g.results[count]['Name'] = ""
        if ("Gender" in i and i['Gender'] == "F"):
            flask.g.results[count]['Restrictions'].append('female.png')
        if ("Veteran" in i and i['Veteran'] == "Y"):
            flask.g.results[count]['Restrictions'].append('veteran.png')
        if ("Disabled" in i and i['Disabled'] == "Y"):
            flask.g.results[count]['Restrictions'].append('disabled.png')
        if ("Food" in i and i["Food"] == "N"):
            del flask.g.results[count]
            continue
        if ("Meal" in i and i['Meal'] != None):
            flask.g.results[count]['Name'] = str("Meals " + i['Meal'] + " at ")
        else:
            # If there aren't any meals, delete the key and entry. Since we're in the format function for meals
            # it's assumed that the service has meals, so since it doesn't, there's no point displaying it.
            del flask.g.results[count]
            continue
        # If the dictionary has a name: check if it's too long
        if ("Name" in i):
            # If it is, add an ellipse to the end
            if (len(i["Name"]) > 36):
                flask.g.results[count]['Name'] += str(i["Name"][:36] + "...")
            # If not, then keep the name as it is (Already have part of a string in this value so we can +=)
            elif (len(i["Name"]) > 0 and flask.g.results[count]['Name'] != ""):
                flask.g.results[count]['Name'] += str(i["Name"])
            # None of the string is formed yet, so we have to create a new one
            else:
                # Put a name into results for display on the site
                flask.g.results[count]['Name'] = str(i["Name"])
        if ("Address" in i and i['Address'] != None):
            flask.g.results[count]['Address'] = i["Address"]
        if ("Phone" in i and i['Phone'] != None):
            flask.g.results[count]['Phone'] = i["Phone"]
        if ("EndpointName" in i and i['EndpointName'] != None):
            flask.g.results[count]['EndpointName'] = i["EndpointName"]

        if len(flask.g.results[count]["Restrictions"]) == 0: #Check if there are any reservations on who can use this clinic
            flask.g.results[count]["Restrictions"].append(True)
        count += 1

    if len(flask.g.results) == 0:
        flask.g.empty = True

def formatClinics(my_list):
    """
    Same as the formatBed function, except it handles clinics.
    """
    flask.g.results = []
    flask.g.empty = False;
    count = 0
    for i in my_list:
        flask.g.results.append({"Restrictions":[]})
        if ("Gender" in i and i['Gender'] == "F"):
            flask.g.results[count]['Restrictions'].append('female.png')
        if ("Veteran" in i and i['Veteran'] == "Y"):
            flask.g.results[count]['Restrictions'].append('veteran.png')
        if ("Disabled" in i and i['Disabled'] == "Y"):
            flask.g.results[count]['Restrictions'].append('disabled.png')
        if ("Clinic" in i and i["Clinic"] == "N"):
            del flask.g.results[count]
            continue
        if ("Name" in i and i['Name'] != None):
            if (len(i["Name"]) > 36):
                flask.g.results[count]["Name"] = str(i["Name"][:36] + "...")
            else:
                flask.g.results[count]['Name'] = str(i["Name"])
        if ("Address" in i and i['Address'] != None):
            flask.g.results[count]['Address'] = i["Address"]
        if ("Phone" in i and i['Phone'] != None):
            flask.g.results[count]['Phone'] = i["Phone"]
        if ("EndpointName" in i and i['EndpointName'] != None):
            flask.g.results[count]['EndpointName'] = i["EndpointName"]

        if len(flask.g.results[count]["Restrictions"]) == 0: #Check if there are any reservations on who can use this clinic
            flask.g.results[count]["Restrictions"].append(True)
        count += 1

    if len(flask.g.results) == 0:
        flask.g.empty = True

@app.route("/search", methods=['POST'])
def search():
    '''
    Checks through the session dictionary to make sure we are passing it the values that needs to be
    displayed on the HTML page.
    '''
    # Get the value of the button press in index.html
    button = flask.request.form.get("sub")
    data_list = []
    out_dict = flask.session["current_dict"].copy()
    # Send user information to the database
    out_dict["Service"] = button
    out_dict["Time"] = str(datetime.datetime.now())
    # Search through the user's dictionary and get rid of all the unnecessary information so that we show
    # all the values the user needs (ie. if a veteran: show all veteran and nonveteran services, but if not
    # a veteran, only show nonveteran services)
    x = data_out.insert_one(out_dict)
    # Clean up the dictionary
    for key, value in list(flask.session["current_dict"].items()):
        if (key == "Veteran" and value == "Y"):
            del flask.session["current_dict"]['Veteran']
        if (key == "Disabled" and value == "Y"):
            del flask.session["current_dict"]['Disabled']
        if (key == "Pets" and value == "N"):
            del flask.session["current_dict"]['Pets']
        if (key == "Family" and value == "Y"):
            del flask.session["current_dict"]['Family']
        if (key == "Gender" and value == "F"):
            del flask.session["current_dict"]['Gender']
        if (key == "Age" and value == "Y"):
            del flask.session["current_dict"]['Age']
    # Clean up the user's dictionary
    for k, v in list(flask.session["current_dict"].items()):
            if v == None:
                del flask.session["current_dict"][k]
    # Make a new dictionary list
    for i in data.find(flask.session["current_dict"]):
        data_list.append(i)
    # If the user wants information on bedding, format the dictionary for bedding info and render the next page
    # The same goes for food and clinics
    if (button == "beds"):
        flask.g.request = "Bedding"
        formatBed(data_list)
        return flask.render_template("userselection.html")
    elif (button == "food"):
        flask.g.request = "Food"
        formatFood(data_list)
        return flask.render_template("userselection.html")
    elif (button == "clinic"):
        flask.g.request = "Clinic"
        formatClinics(data_list)
        return flask.render_template("userselection.html")
    return flask.render_template("userselection.html")

@app.route("/search_es", methods=['GET','POST'])
def search_es():
    '''
    Checks through the session dictionary to make sure we are passing it the values that needs to be
    displayed on the HTML page.
    '''
    # Get the value of the button press in index.html
    button = flask.request.form.get("sub")
    data_list = []
    out_dict = flask.session["current_dict"].copy()
    # Send user information to the database
    out_dict["Service"] = button
    out_dict["Time"] = str(datetime.datetime.now())
    # Search through the user's dictionary and get rid of all the unnecessary information so that we show
    # all the values the user needs (ie. if a veteran: show all veteran and nonveteran services, but if not
    # a veteran, only show nonveteran services)
    x = data_out.insert_one(out_dict)
    # Clean up the dictionary
    for key, value in list(flask.session["current_dict"].items()):
        if (key == "Veteran" and value == "Y"):
            del flask.session["current_dict"]['Veteran']
        if (key == "Disabled" and value == "Y"):
            del flask.session["current_dict"]['Disabled']
        if (key == "Pets" and value == "N"):
            del flask.session["current_dict"]['Pets']
        if (key == "Family" and value == "Y"):
            del flask.session["current_dict"]['Family']
        if (key == "Gender" and value == "F"):
            del flask.session["current_dict"]['Gender']
        if (key == "Age" and value == "Y"):
            del flask.session["current_dict"]['Age']
    # Clean up the user's dictionary
    for k, v in list(flask.session["current_dict"].items()):
            if v == None:
                del flask.session["current_dict"][k]
    # Make a new dictionary list
    for i in data.find(flask.session["current_dict"]):
        data_list.append(i)
    # If the user wants information on bedding, format the dictionary for bedding info and render the next page
    # The same goes for food and clinics
    if (button == "beds"):
        flask.g.request = "Bedding"
        formatBedEs(data_list)
        return flask.render_template("userselection_es.html")
    elif (button == "food"):
        flask.g.request = "Food"
        formatFood(data_list)
        return flask.render_template("userselection_es.html")
    elif (button == "clinic"):
        flask.g.request = "Clinic"
        formatClinics(data_list)
        return flask.render_template("userselection_es.html")
    return flask.render_template("userselection_es.html")

@app.route("/ees", methods=['GET'])
def eesMap():
    return flask.render_template("ees.html")

@app.route("/shs", methods=['GET'])
def shsMap():
    return flask.render_template("shs.html")

@app.route("/css", methods=['GET'])
def cssMap():
    return flask.render_template("css.html")

@app.route("/em", methods=['GET'])
def emMap():
    return flask.render_template("em.html")

@app.route("/sheltercare", methods=['GET'])
def sheltercareMap():
    return flask.render_template("sheltercare.html")

@app.route("/ws", methods=['GET'])
def womensspaceMap():
    return flask.render_template("ws.html")

@app.route("/ffl", methods=['GET'])
def fflMap():
    return flask.render_template("ffl.html")

@app.route("/mainmap", methods=['GET'])
def mainMap():
    return flask.render_template("mainmap.html")


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
