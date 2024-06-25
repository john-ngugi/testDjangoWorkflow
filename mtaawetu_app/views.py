from django.shortcuts import render
import json
import folium
from folium import Html, Element
import json
import requests
import psycopg2
from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd
import decimal
from django.http import JsonResponse
from django.utils.http import urlencode
from django.urls import reverse
from django.contrib import messages
import branca
# Function to randomize color selection

import random
# Create your views here.

layer_options=['schoolaccessindexdrive','schoolaccessindexwalk', 'schoolaccessratiodrive',
             'schoolaccessratiowal','nbihealthaccess','nbijobsacces','nbilanduseentropy','sdna_1500meters_2018','sdna_1000meters_2018','sdna_500meters_2018']

legend_options = options=['school access Index', 'school access index drive', 'school access index walk',
                          'school access', 'school access ratio', 'school access ratio walk', 'school access ratio',
                          "health access index",
                          "health access ratio",'Job access index','Job access ratio','land use Entropy','sdna_1500meters_2018',
                          'sdna_1000meters_2018','sdna_500meters_2018']

attribute_options = ["schoolacce", 'saccinddrv', 'schaccessb','saccindwlk','jobaccindx','jobacratio','accessindx','acessratio','areahex','entropy_fn',"JobAccesRatio",'shape_leng']

layers_dict = {
    'schoolaccessindexwalk': 'school index walk',
    'schoolaccessindexdrive': 'school index drive',
    'schoolaccessratiodrive': 'school access ratio drive',
    'schoolaccessratiowalk': 'school access ratio walk',  # Corrected typo from 'schoolaccessratiowal'
    'nbijobsacces_index': 'job access index',  # Renamed to ensure uniqueness
    'nbijobsacces_ratio': 'job access ratio',  # Renamed to ensure uniqueness
    'nbilanduseentropy_areahex': 'areahex',  # Renamed to ensure uniqueness
    'nbilanduseentropy_fn': 'entropy_fn',  # Renamed to ensure uniqueness
    'nbihealthaccess_index': 'Nairobi Health Access Index',  # Renamed to ensure uniqueness
    'nbihealthaccess_ratio': 'Nairobi Health Access Ratio',  # Renamed to ensure uniqueness
    'sdna_1500meters_2018': 'Spatial design network analysis 1.5Km',
    'sdna_1000meters_2018': 'Spatial Design Network Analysis 1km',
    'sdna_500meters_2018': 'Spatial Design Network Analysis 500m'
}

def filterLayers(layer_name, attribute_name):
    if layer_name == 'nbijobsacces_index' and attribute_name == 'jobaccindx':
        table_name = 'nbijobsaccess'
    if layer_name == 'nbijobsacces_ratio' and attribute_name == 'jobacratio':
        table_name = 'nbijobsaccess'


    if layer_name == 'nbilanduseentropy_areahex' and attribute_name == 'areahex':
        table_name = 'nbilanduseentropy'
    if layer_name == 'nbilanduseentropy_fn' and attribute_name == 'entropy_fn':
        table_name = 'nbilanduseentropy'


    if layer_name == 'nbihealthaccess_index' and attribute_name == 'accessindx':
        table_name = 'nbihealthaccess'

    if layer_name == 'nbihealthaccess_ratio' and attribute_name == 'acessratio':
        table_name = 'nbihealthaccess'
    print(table_name)
    return table_name

# Define the custom tile layer URL and name
custom_tile_url = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}{r}.png'
custom_tile_name = 'CartoDB Voyager'


base_maps = {
    "CartoDB Positron": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    "CartoDB Dark Matter": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    "OpenStreetMap": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
}

# Function to generate star rating HTML
def generate_star_rating(rating):
    stars = ''
    for i in range(5):
        if i < rating:
            stars += '<i class="fa-solid fa-star " aria-hidden="true" style="color: #FFD43B;"></i>'
        else:
            stars += '<i class="fa-regular fa-star" aria-hidden="true" style="color: #FFD43B;"></i>'
    return stars

def get_db_connection():
    return psycopg2.connect(
        dbname='mtaa-wetu0_start',
        user= 'mtaa-wetu0',
        password='MtaaWetu***',
        host='postgresql-mtaa-wetu0.alwaysdata.net',
        port='5432'
    )
conn = get_db_connection()

# Database connection URL
db_connection_url = "postgresql://mtaa-wetu0:MtaaWetu***@postgresql-mtaa-wetu0.alwaysdata.net:5432/mtaa-wetu0_start"
con = create_engine(db_connection_url)


# Define a function to generate different colors based on the feature properties
def get_color(properties):
    # Convert Decimal objects to float, if applicable
    properties = {key: str(value) if isinstance(value, decimal.Decimal) else value for key, value in properties.items()}
    # Assuming you have a different property or combination of properties to use for generating colors
    # Here, I'm just using a hash of the properties to generate a color
    hue = hash(json.dumps(properties)) % 360
    saturation = 50
    lightness = 50
    return f'hsl({hue}, {saturation}%, {lightness}%)'



#define the function to create the featues
def get_features_geojson(m,tableName,layername,extra_columns=[]):
    """

    Args:
      tableName: Name of the database table to query
      layername: Name of the layer name to add to the map
      extra_columns: List of columns to include in the GeoJSON feature properties.
    """



    table_name = tableName
    print(table_name)
    cursor = conn.cursor()
    # Create a cursor to execute SQL queries
    with cursor:

        # Join all the columns specified in *args into a comma-separated string
        columns_str = ', '.join(extra_columns)

        # Start a transaction
        cursor.execute("BEGIN")

        # Query to fetch all features and transform the geometry to GeoJSON
        sql_query = f'SELECT ST_AsGeoJSON(ST_ForcePolygonCCW(geom)) AS geometry, {columns_str} FROM {table_name};'

        cursor.execute("ROLLBACK")
        conn.commit()
        cursor.execute(sql_query)

        # Fetch all rows
        rows = cursor.fetchall()

        # create the GeoJson file structure to avoid unaccepted geoJson
        geojson_data = {
            "type": "FeatureCollection",
            "features": []
        }

        #loop through all the rows in the columns and append to the GeoJson dictionary
        for row in rows:
            try:
                # Parse the geometry as GeoJSON
                # add the properties given in the *args(extra columns)

                properties = {}
                for i, column in enumerate(extra_columns, 1):
                    properties[column] = str(row[i])

                feature = {
                    "type": "Feature",
                    "geometry": json.loads(row[0]),
                    "properties": properties
                }
                geojson_data["features"].append(feature)

            except (json.JSONDecodeError, TypeError) as e:
                # Handle the error
                print(f"Error decoding JSON for row: {row}. Error: {e}")

        if geojson_data['features'][0]["geometry"]['type'] == 'MultiPolygon':
            folium.GeoJson(
                geojson_data,
                name=layername,
                style_function=lambda feature: {
                    "fillColor": get_color(feature['properties']),
                    "color": "grey",      # Outline color
                    "weight": 1,          # Outline weight
                    "fillOpacity": 0.9    # Transparency of fill color
                },
                highlight_function=lambda feature: {
                    "fillColor": "red",   # Color for highlighted feature
                    "color": "white",
                    "weight": 2,
                    "fillOpacity": 0.6
                },
                tooltip=folium.GeoJsonTooltip(fields=extra_columns, aliases=extra_columns)
            ).add_to(m)
            print("success: geojson")
        elif geojson_data['features'][0]["geometry"]['type'] == 'MultiLineString':
            folium.GeoJson(
                geojson_data,
                name=layername,
                style_function=lambda feature: {
                    "color": "blue",    # Line color
                    "weight": 3,        # Line weight
                    "opacity": 0.7      # Line opacity
                },
                highlight_function=lambda feature: {
                    "color": "yellow",  # Highlighted line color
                    "weight": 5,        # Highlighted line weight
                    "opacity": 1        # Highlighted line opacity
                },
                tooltip=folium.GeoJsonTooltip(fields=extra_columns, aliases=extra_columns)
            ).add_to(m)


        else:
            print('Layer is neither MultiPolygon nor MultiLineString')
            return m

        return 'success'

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

def getPointData(m,marker_group,lat,lon, table_name,extra_columns=[]):
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
  tablename = f'{table_name}'
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
    # Generate star rating HTML
    # star_rating = generate_star_rating(row['rating'])
    star_rating = generate_star_rating(2)
    #integrating the toggle functionality within the popup HTML
    popup_html = f"""
    <div class="card border-0 shadow-md" style="width: 20rem;">
        <div class="card-body">
            <h5 class="card-title">{row['f_name']}</h5>
            <p> Location: {row['location']}</p>
            <p> Division: {row['division']}</p>
            <div>Level of Satisfaction: {star_rating}</div>
            <a href="#" class="stretched-link" id="box-opener-{index}" onclick="openCommentsBox({index})">View and add comment</a>

        </div>
    </div>
    """

    # Create a Marker with the formatted popup
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        tooltip=row['f_name'],
        popup=folium.Popup(popup_html, max_width=2650),
        icon=folium.Icon(color='green'),
    ).add_to(marker_group)
    # Add the feature group to the map
    marker_group.add_to(m)
    # Add JavaScript to the map
    js = """
<script>
    function openCommentsBox(index) {
        var commentsBox = document.getElementById('comments');
        commentsBox.style.display = 'flex';
    }

    function closeCommentsBox(index) {
        var commentsBox = document.getElementById('comments');
        commentsBox.style.display = 'none';
    }
    </script>

    """
    m.get_root().html.add_child(folium.Element(js))
  print("Markers added")
  return m



def create_chloropeth(m,marker_group,table_name,legend_name,extra_columns=[]):
    '''
    table_name: string: Database table name
    legend_name: string: Name of the legend
    extra_columns: list: other attributes to be returned
    '''
    if table_name == 'nbihealthaccess':
        getPointData(m=m,marker_group=marker_group,lat='latitude',lon='longitude',table_name='nairobi_hospitals',extra_columns=['f_name', 'location','agency','division'])


    # Join all the columns specified in *args into a comma-separated string
    columns_str = ', '.join(extra_columns)
    # set the table name
    #'\"nairobi_roads\"'
    tablename = f'{table_name}'
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

        #  Create custom CSS
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

        # Inject custom CSS into the map
        css_element = Element(custom_css)
        m.get_root().html.add_child(css_element)

        folium.LayerControl().add_to(m)
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(fields=extra_columns, aliases= extra_columns, localize=True)
        )


      ####### overpass API #########
        if table_name == 'schoolaccessindexdrive' or\
            table_name == 'schoolaccessindexwalk' or table_name == 'schoolaccessratiodrive' \
            or table_name == 'schoolaccessratiowalk':
            amenity = 'school'
        elif table_name == 'nbihealthaccess':
            amenity ='hospital'
        else:
            amenity == 'hospital'

        # Define parameters
        radius = 25000
        latitude = -1.2921
        longitude = 36.8219
        amenity_type = f"amenity={amenity}"

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
                # Generate star rating HTML
                star_rating = generate_star_rating(i['tags'].get('rating', 0))

                # Define the HTML for the popup using Bootstrap card
                popup_html = f"""
                <div class="card border-0 shadow-md" style="width: 20rem;">
                <div class="card-body">
                    <h5 class="card-title">{i['tags']['name']}</h5>
                    <p class="card-text">{i['tags'].get('description', 'No description available')}</p>
                    <div>Level of Satisfaction: {star_rating}</div>
                    <a href="#" class="stretched-link"> View and add comment </a>
                </div>
                </div>
                """

                # Create a Marker with the formatted popup
                folium.Marker(
                    location=[i['lat'], i['lon']],
                    tooltip=i['tags']['name'],
                    popup=folium.Popup(popup_html, max_width=2750),
                    icon=folium.Icon(color="red"),
                ).add_to(marker_group)

            else:
                print("No elements Available ")
        # Handle any errors
        else:
            print("Error:", response.status_code)
        return m
    except:
      return 'error with the Query check the parameters and try again '

def newIndex(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        go_ahead = data.get('send')
        if go_ahead:
            base_url = reverse('home')
            print('reverse finished')
            # return redirect(f"{base_url}?{urlencode({'coordinates': json.dumps(coordinates)})}")
            return JsonResponse({'url': f"{base_url}?{urlencode({'pass': json.dumps(go_ahead)})}"})
    return render(request,'base.html',)




def index(request):
    print("runing...")
    m = folium.Map(
                   location = (-1.2921, 36.8219),
                   zoom_control=False,
                   zoom_start=12,
                    width='100%',
                    height='100%')

    # Add the custom base map tile layer with a custom name
    folium.TileLayer(
        tiles=custom_tile_url,
        name=custom_tile_name,
        attr='CartoDB'
    ).add_to(m)


    marker_group = folium.FeatureGroup(name='Service buildings',show=False)

    # connect to the database
    # create_chloropeth(m,'estates_nairobi','area',extra_columns=['name','shape_area'])
    getPointData(m=m,marker_group=marker_group ,lat='latitude',lon='longitude',table_name='nairobi_hospitals',extra_columns=['f_name', 'location','agency','division'])
    create_chloropeth(m=m,marker_group=marker_group,table_name="schoolaccessindexdrive",legend_name='school access Index',extra_columns=['id','schoolacce'])
    # Add layer control to the map
    # f=folium.Figure(height="100%")
    # m.add(f)
    print("I am getting the layers! ")
    context = {
        'map': m._repr_html_(),
        'layer_options': layers_dict,
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
    marker_group = folium.FeatureGroup(name='service Buildings',show=False)
    if request.method == 'POST':

        # Process POST data

        data = json.loads(request.body)
        table_name = data.get('layerSelect')
        legend_name = table_name
        attribute = data.get('attributeSelect')
        table_name = filterLayers(table_name,attribute)
        print(table_name)

        if table_name == 'sdna_1500meters_2018' or table_name == 'sdna_1000meters_2018' or table_name == 'sdna_500meters_2018':
            print(table_name)
            get_features_geojson(m,f'{table_name}',layername=legend_name,extra_columns=['id',f'{attribute}'])
        else:
            create_chloropeth(m=m,marker_group=marker_group, table_name=table_name,legend_name=legend_name,extra_columns=['id',f'{attribute}'])

        print(data)
        context = {
            'map': m._repr_html_(),
            'layer_options': layer_options,
            'legend_options': legend_options,
            'attribute_options': attribute_options,
        }

        # Return a response after processing POST data
        return JsonResponse(context, safe = True)


    # If not a POST request (e.g., GET request), render 'base.html'
    return render(request, 'base.html')


def loading(request):
    return render(request,'loaders/mainpage.html')
