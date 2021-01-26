from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""

    
    plants_data = mongo.db.plants.find({})

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        
        new_plant = {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted')
        }
        
        insert_plant = mongo.db.plants.insert_one(new_plant)
        return redirect(url_for('detail', plant_id= insert_plant.inserted_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})
    
    harvests = mongo.db.plants.find({'plant_id': plant_id})

    context = {
        'plant' : plant_to_show,
        'harvests': harvests,
        'plant_id': ObjectId(plant_id),
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """

    # Create a new harvest object by passing in the form data from the
    # detail page form.
    new_harvest = {
        'quantity': request.form.get('harvested_amount'), # e.g. '3 tomatoes'
        'date': request.form.get('date_harvested'),
        'plant_id': ObjectId(plant_id)
    }

    
    mongo.db.harvests.insert_one(new_harvest)
    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        plant_name = request.form.get('plant_name')
        photo = request.form.get('photo')
        date_planted = request.form.get('date_planted')
        variety = request.form.get('variety')
        # Make an `update_one` database call to update the plant with the
        # given id. Make sure to put the updated fields in the `$set` object.
        mongo.db.plants.update_one({
            '_id': ObjectId(plant_id)
        },
            {
            '$set': { 
                '_id': ObjectId(plant_id),
                'plant_name' : plant_name,
                'date_planted' : date_planted,
                'variety' : variety,
                'photo_url' : photo
            }
        })
        
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        # Make a `find_one` database call to get the plant object with the
        # passed-in _id.
        plant_to_show = mongo.db.plants.find_one({
            '_id' : ObjectId(plant_id)
        })

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    #  Make a `delete_one` database call to delete the plant with the given
    # id.

    mongo.db.plants.delete_one({'id': ObjectId(plant_id)})

    # Also, make a `delete_many` database call to delete all harvests with
    # the given plant id.

    mongo.db.harvests.delete_many({"_id": ObjectId(plant_id)})

    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)