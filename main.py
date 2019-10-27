import os

import urllib

from google.cloud import vision
from google.cloud.vision import types
from firebase import Firebase

import requests
import json



# Google Vision API creds
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'creds.json'


# Firebase configuration
config = {
    "apiKey": "AIzaSyDQ1lcaiMTXR3Dmey9VY_gFJK2mt05MMds",
    "authDomain": "recipify-c54b7.firebaseapp.com",
    "databaseURL": "https://recipify-c54b7.firebaseio.com",
    "storageBucket": "recipify-c54b7.appspot.com"
}

firebase = Firebase(config)



def get_image():

    # Get data from Firebase and make it an Image

    db = firebase.database()
    users = db.child("url").get()
    url = users.val()
    resp = urllib.request.urlopen(url)
    response = requests.get(url)
    img = bytes(response.content)

    return img


def send_data(output):

    db = firebase.database()

    db.child("result/two").set(output)   

    return "Data Sent"



def get_food_nutrients(food):

    # Get nutrients details of a food from NUTRIONIX API

    url = "https://nutritionix-api.p.rapidapi.com/v1_1/search/{}".format(food)

    querystring = {"fields": "item_name,nf_calories,nf_total_fat"}

    headers = {
        'x-rapidapi-host': "nutritionix-api.p.rapidapi.com",
        'x-rapidapi-key': "e4573ac34fmshc71719554be1369p1d0fcajsnc45c98c12e74"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    # print(response.text)

    output = response.json()

    calories = []
    fat = []

    hits = output["hits"]
    calories = hits[0]["fields"]["nf_calories"]
    fat = hits[0]["fields"]["nf_total_fat"]

    nutrients = {"calories": calories,
                 "fat": fat}


    return calories, fat



def get_food_details(food):


    # Gets food ingredients and recipe from RECIPY PUPPY

    url = "https://recipe-puppy.p.rapidapi.com/"

    headers = {
        'x-rapidapi-host': "recipe-puppy.p.rapidapi.com",
        'x-rapidapi-key': "e4573ac34fmshc71719554be1369p1d0fcajsnc45c98c12e74"
    }

    querystring = {"q": str(food)}

    response = requests.request("GET", url, headers=headers, params=querystring)

    output = response.json()

    # print(output['results'])
    ingredients = []
    names = []
    recepies = []
    count = 0

    for food in output['results']:
        content = food['ingredients'].split(',')
        names.append(food['title'])
        recepies.append(food['href'])
        ingredients = ingredients + content

        count = count+1
        if(count > 2):
            break

    # res = dict(zip(names, recepies))

    # print(str(res))


    return names, recepies, ingredients




def object_detect(img):

    # Uses Google Vision API to return a json file containing prediction and localization data

    client = vision.ImageAnnotatorClient()

    image = vision.types.Image(content = img)
    response = client.label_detection(image = image)

    output = response.label_annotations

    print("################################")

    names = []
    length_breadth = []
    recipe_names = []
    recepies = []
    ingredients = []
    calories = []
    fats = []

    print(output)

    #for obj in output:

        ## TODO: Have to use implement the API functions here.

    obj = output[0]

    if (obj.description == 'Food' or obj.description == 'Dish'):

        obj = output[1]

        if (obj.description == 'Food' or obj.description == 'Dish'):

            obj = output[2]

        

    #print(obj.name)
    #names.append(obj.name)
    recepie_name, recepie, ingredient = get_food_details(obj.description)
    #recipe_names.append(recepie_name)
    #recepies.append(recepie)
    #ingredients.append(ingredient)
    calorie, fat = get_food_nutrients(obj.description)
    #calories.append(calorie)
    #fats.append(fat)
    #print(obj.bounding_poly.normalized_vertices)
    #bounding_boxes.append([(obj.bounding_poly.normalized_vertices[0].x, obj.bounding_poly.normalized_vertices[0].y)])

    value = {'names' : obj.description,
            'recepie_names' : recepie_name,
            'recepies' : recepie,
            'ingredients' : ingredient,
            'calories' : calorie,
            'fat' : fat,}
    

    #with open('data.json', 'w') as f:

    #    json.dump(value,f)


    return value



def send_json():

    img = get_image()
    print("Got Image")
    output = object_detect(img)
    #print(output)
    send_data(output)


    return "Data Updates to firebase"

if(__name__ == '__main__'):

    while(True):

        db = firebase.database()

        check_val = db.child("check").get().val()


        if(check_val == 1):

            send_json()

            db.child("check").set(0)