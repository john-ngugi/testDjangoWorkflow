from django.shortcuts import render
import json
import folium
from folium import Html, Element
import json
import requests
from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd
import requests
from django.http import JsonResponse
from django.contrib import messages
# Function to randomize color selection

import random
# Create your views here.

layer_options=['schoolaccessindexdrive','schoolaccessindexwalk', 'schoolaccessratiodrive',
             'schoolaccessratiowal','nbihealthaccess','nbijobsacces','nbilanduseentropy','public.schoolaccessratiowalk']

legend_options = options=['school access Index', 'school access index drive', 'school access index walk',
                          'school access', 'school access ratio', 'school access ratio walk', 'school access ratio', "health access index","health access ratio",' Job access index','Job access ratio','land use Entropy']
attribute_options = ["schoolacce", 'saccinddrv', 'schaccessb','saccindwlk','jobaccindx','jobacratio','accessindx','acessratio','areahex','entropy_fn',"JobAccesRatio"]

# Define the custom tile layer URL and name
custom_tile_url = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}{r}.png'
custom_tile_name = 'CartoDB Voyager'


base_maps = {
    "CartoDB Positron": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    "CartoDB Dark Matter": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    "OpenStreetMap": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
}



# Database connection URL
db_connection_url = "postgresql://mtaa-wetu0:MtaaWetu***@postgresql-mtaa-wetu0.alwaysdata.net:5432/mtaa-wetu0_start"
con = create_engine(db_connection_url)


color_values = [
    "YlGn",
    "YlGnBu",
    "GnBu",
    "BuGn",
    "PuBu",
    "PuBuGn",
    "BuPu",
    "RdPu",
    "PuRd",
    "OrRd",
    "YlOrRd",
    "YlOrBr",
    "Purples",
    "Blues",
    "Greens",
    "Oranges",
    "Reds"
]



def getRandomColor():
  color = color_values[random.randint(0,len(color_values))-1]
  return color

def getPointData(m,lat,lon, table_name,extra_columns=[]):
  '''
  lat: string: latitide
  lon: string: longitude
  table_name: string: Database table name
  extra_columns: list: other attributes to be returned
  '''
  # get the connection url from the database
  db_connection_url = "postgresql://mtaa-wetu0:MtaaWetu***@postgresql-mtaa-wetu0.alwaysdata.net:5432/mtaa-wetu0_start"

  # create the connection engine
  db_conn = create_engine(db_connection_url)

  # Join all the columns specified in *args into a comma-separated string
  columns_str = ', '.join(extra_columns)
  # set the table name
  tablename = f'\{table_name}'
  # get the connection url from the database
  sql = f'SELECT {lat},{lon}, {columns_str} FROM {table_name}'
  columns = [lat,lon] + extra_columns
  # create the geodataframe
  sql_query = pd.read_sql_query(sql, db_conn)
  # print(sql_query)
  df = pd.DataFrame(sql_query, columns=columns)
  #drop any null values
  df = df.dropna()

  for index, row in df.iterrows():
    # print(row['latitude'],row['longitude'])
    folium.Marker(
        location= [row['latitude'], row['longitude']],
        tooltip=row['f_name'],
        popup=row['f_name'],
        icon=folium.Icon(color='green'),
    ).add_to(m)
  print("Markers added")
  return m



def create_chloropeth(m,table_name,legend_name,extra_columns=[]):
    '''
    table_name: string: Database table name
    legend_name: string: Name of the legend
    extra_columns: list: other attributes to be returned
    '''
    if table_name == 'nbihealthaccess':
        getPointData(m=m,lat='latitude',lon='longitude',table_name='nairobi_hospitals',extra_columns=['f_name', 'location','agency'])


    # Join all the columns specified in *args into a comma-separated string
    columns_str = ', '.join(extra_columns)
    # set the table name
    #'\"nairobi_roads\"'
    tablename = f'\{table_name}'
    # get the connection url from the database
    db_connection_url = "postgresql://mtaa-wetu0:MtaaWetu***@postgresql-mtaa-wetu0.alwaysdata.net:5432/mtaa-wetu0_start"

    # create the connection engine
    con = create_engine(db_connection_url)

    try:
        #run the sql query to postGIS
        sql = f'SELECT geom, {columns_str} FROM {table_name}'

        #create the geodataframe
        df = gpd.GeoDataFrame.from_postgis(sql, con)
        #drop any null values
        df = df.dropna()
        # Convert columns starting from the third column to float
        df[df.columns[2:]] = df[df.columns[2:]].astype(float)
        key_on = extra_columns[0]
        # Create the choropleth layer
        choropleth = folium.Choropleth(
            geo_data=df, # Data to be used
            data=df,  # Data to be used
            columns= extra_columns,  # Column with area names and numeric values
            key_on=f"feature.properties.{key_on}",  # Key to match GeoDataFrame with GeoJSON features
            fill_color= getRandomColor(),  # Color scheme for the map
            fill_opacity=0.7,  # Opacity of the fill color
            line_opacity=0.2,  # Opacity of the border lines
            legend_name=legend_name,  # Name of the legend
            name= table_name,
            # threshold_scale=custom_scale,  # Custom threshold scale(removed due to abnormal data distribution)
            bins=5,  # Number of bins for the scale
        ).add_to(m)
        # Step 2: Create custom CSS
        custom_css = """
        <style>
        .leaflet-control-layers {
            background-color: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.4);
            font-family: 'Arial', sans-serif;
        }

        .leaflet-control-layers-toggle {
            color: #333;
            background-color: #f8f9fa;
            border: 1px solid #ccc;
            border-radius: 3px;
            padding: 5px 10px;
            font-size: 14px;
            cursor: pointer;
        }

        .leaflet-control-layers-list {
            padding: 0;
            margin: 0;
            list-style: none;
        }

        .leaflet-control-layers-base,
        .leaflet-control-layers-overlays {
            margin-bottom: 10px;
        }

        .leaflet-control-layers-separator {
            border-top: 1px solid #ccc;
            margin-top: 10px;
            margin-bottom: 10px;
            padding-top: 5px;
        }
        </style>
        """

        # Step 3: Inject custom CSS into the map
        css_element = Element(custom_css)
        m.get_root().html.add_child(css_element)

        folium.LayerControl().add_to(m)
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(fields=extra_columns, aliases= extra_columns, localize=True)
        )


      ####### overpass API #########

        # Define parameters
        radius = 25000
        latitude = -1.2921
        longitude = 36.8219
        amenity_type = "amenity=hospital"

        # Define the Overpass query string
        overpass_query = f"""
        [out:json];
        (
            node(around:{radius},{latitude},{longitude})[{amenity_type}];
        );
        out body;
        >;
        out skel qt;
        """


        # Send the query to the Overpass API
        url = 'https://overpass-api.de/api/interpreter'
        response = requests.post(url, data=overpass_query)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # check if elements are available
            if data['elements']:
                print('success')
                for i in data['elements']:
                    folium.Marker(
                        location= [i['lat'], i['lon']],
                        tooltip=i['tags']['name'],
                        popup=i['tags']['name'],
                        icon=folium.Icon(color="red"),
                    ).add_to(m)
            else:
                print("No elements Available ")
        # Handle any errors
        else:
            print("Error:", response.status_code)
        return m
    except:
      return 'error with the Query check the parameters and try again '






def index(request):

    m = folium.Map(
                   location = (-1.2921, 36.8219),
                   zoom_control=False,
                   zoom_start=12)

    # Add the custom base map tile layer with a custom name
    folium.TileLayer(
        tiles=custom_tile_url,
        name=custom_tile_name,
        attr='CartoDB'
    ).add_to(m)
    # connect to the database
    # create_chloropeth(m,'estates_nairobi','area',extra_columns=['name','shape_area'])
    getPointData(m=m,lat='latitude',lon='longitude',table_name='nairobi_hospitals',extra_columns=['f_name', 'location','agency'])
    create_chloropeth(m=m,table_name="schoolaccessindexdrive",legend_name='school access Index',extra_columns=['id','schoolacce'])
    context = {
        'map': m._repr_html_(),
        'layer_options': layer_options,
        'legend_options': legend_options,
        'attribute_options': attribute_options,

    }

    return render(request,'base.html',context)

def getLayers(request):

    m = folium.Map(
                location = (-1.2921, 36.8219),
                zoom_control=False,
                zoom_start=12)
    folium.TileLayer(
        tiles=custom_tile_url,
        name=custom_tile_name,
        attr='CartoDB'
    ).add_to(m)

    if request.method == 'POST':
        # Process POST data here if needed
        # Example: Assuming you want to extract data from JSON request body
        import json
        data = json.loads(request.body)
        table_name = data.get('layerSelect')
        legend_name = data.get('layerNameSelect')
        attribute = data.get('attributeSelect')

        create_chloropeth(m=m,table_name=table_name,legend_name=legend_name,extra_columns=['id',f'{attribute}'])
        print(data)
        context = {
            'map': m._repr_html_(),
            'layer_options': layer_options,
            'legend_options': legend_options,
            'attribute_options': attribute_options,
        }
            # Return a response after processing POST data
        return JsonResponse(context, safe = True)


    # If not a POST request (e.g., GET request), render 'index.html'
    return render(request, 'base.html')
