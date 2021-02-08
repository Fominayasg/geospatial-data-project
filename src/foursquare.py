import requests
import json
import pandas as pd
from functools import reduce
import operator
import geopandas as gpd
import shapely.geometry
from pymongo import MongoClient,GEOSPHERE
client = MongoClient("mongodb://localhost:27017/ironhack")



def api_to_geopd (api_code,limit,tok1,tok2):

    url_query = 'https://api.foursquare.com/v2/venues/explore'
    in_lat = 37.7825098
    in_long = -122.4077973

    parametros ={"client_id" : tok1,
            "client_secret" : tok2,
            "v" : "20180323",
             "ll": f"37.7825098, -122.4077973",
             "query" :api_code,
             "limit": limit
            }
    
    resp = requests.get(url = url_query, params=parametros)
    data = json.loads(resp.text)
    decoding_data = data.get ("response")
    decoded = decoding_data.get("groups")[0]
    my_items = decoded.get("items")

    mapa_nombre = ["venue", "name"]
    m_latitude = ["venue", "location", "lat"]
    m_longitude = ["venue", "location", "lng"]

    def getFromDict(diccionario,mapa):
        return reduce(operator.getitem,mapa,diccionario)

    all_the_items =[]
    for dic in my_items:
        items_dict = {}
        items_dict["name"] = getFromDict(dic,mapa_nombre)
        items_dict["latitud"] = getFromDict(dic,m_latitude)
        items_dict["longitud"] = getFromDict(dic,m_longitude)
        all_the_items.append(items_dict)
    
    dataframefinal = pd.DataFrame(all_the_items)
    

    gdf = gpd.GeoDataFrame(dataframefinal,geometry = gpd.points_from_xy(dataframefinal.longitud, dataframefinal.latitud))

    return gdf



def gpd_to_geojson(gdf,nombre):
    gdf['geometry']=gdf['geometry'].apply(lambda x:shapely.geometry.mapping(x))

    stb = client.ironhack
    collection = stb[f"{nombre}"]
    collection.create_index([("geometry", GEOSPHERE)])

    data = gdf.to_dict(orient='records')
    collection.insert_many(data)
        
    return f"{nombre}collection created"



    
    
'''REVISAR: NO FUNCIONA
def nearest (geojson,loc):
    cercano = stb.geojson.find({"geometry":{"$near":{"type":"Point", "coordinates":loc}}})
    return list(cercano)'''