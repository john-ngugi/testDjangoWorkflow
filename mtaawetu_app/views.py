from django.shortcuts import render,get_object_or_404
import json
import folium
from folium import Html, Element
import json
import requests
import psycopg2
from shapely.geometry import Point
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import geopandas as gpd
import pandas as pd
import decimal
from django.http import JsonResponse
from django.utils.http import urlencode
from django.urls import reverse
from django.contrib import messages
import branca.colormap as cm
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
# from . import models
from .models import Amenities,Satisfaction,Research
from django.conf import settings
import os
from pathlib import Path

import random
# Create your views here.

BASE_DIR = Path(__file__).resolve().parent.parent
def getLayercontrol(m):
    # Create custom CSS
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
    css_element = folium.Element(custom_css)
    m.get_root().html.add_child(css_element)

    # Inject custom JavaScript for sliders
    slider_js = """
    <script>
    function createSlider(layerName, index) {
        var slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '0';
        slider.max = '1';
        slider.step = '0.1';
        slider.value = '1';
        slider.style.width = '100px';
        slider.style.margin = '5px';

        slider.oninput = function() {
            var layers = document.querySelectorAll('input[type="checkbox"][title="' + layerName + '"]');
            if (layers.length > 0) {
                var layerId = layers[0].id.replace(/-/g, '_');
                var mapLayer = window[layerId];
                if (mapLayer) {
                    mapLayer.eachLayer(function(layer) {
                        layer.setStyle({opacity: slider.value, fillOpacity: slider.value});
                    });
                }
            }
        };

        return slider;
    }

    document.addEventListener('DOMContentLoaded', function() {
        var layers = document.querySelectorAll('.leaflet-control-layers-overlays label span');
        layers.forEach(function(layer, index) {
            var layerName = layer.innerText;
            var slider = createSlider(layerName, index);
            layer.parentElement.appendChild(slider);
        });
    });
    </script>
    """

    # Add the JavaScript to the map
    js_element = folium.Element(slider_js)
    m.get_root().html.add_child(js_element)
    return 'control success'

layer_options=['schoolaccessindexdrive','schoolaccessindexwalk', 'schoolaccessratiodrive',
            'schoolaccessratiowal','nbihealthaccess','nbijobsacces','nbilanduseentropy','sdna_1500meters_2018','sdna_1000meters_2018','sdna_500meters_2018']

legend_options = options=['school access Index', 'school access index drive', 'school access index walk',
                        'school access', 'school access ratio', 'school access ratio walk', 'school access ratio',
                        "health access index",
                        "health access ratio",'Job access index','Job access ratio','land use Entropy','sdna_1500meters_2018',
                        'sdna_1000meters_2018','sdna_500meters_2018']

attribute_options = ["schoolacce", 'saccinddrv', 'schaccessb','saccindwlk','jobaccindx','jobacratio','accessindx','acessratio','areahex','entropy_fn',"JobAccesRatio",'shape_leng']

def filterLayers(layer_name,attribute_name):
    print(layer_name == 'Healthcare Accessibility')
    if layer_name == 'Jobs accessibility':
        attribute_name = ['jobaccindx','subcounty','wards','population']
        table_name = 'nbijobsacces'

    elif layer_name == 'Land use mix' :
        attribute_name = ['entropy_fn','subcounty','wards','population']
        table_name = 'nbilanduseentropy'


    elif layer_name == 'Healthcare Accessibility':
        attribute_name = ['accessindx','subcounty','wards','population']
        table_name = 'nbihealthaccess'



    elif layer_name == 'School accessibility':
        attribute_name = ['schoolacce','subcounty','wards','population']
        table_name = 'schoolaccessindexwalk'

    else:
        table_name = layer_name
        attribute_name = "None"

    print("table name", table_name)
    return table_name,attribute_name

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

# Function to randomize color selection
def get_color(properties):
    # Convert Decimal objects to float, if applicable
    properties = {key: str(value) if isinstance(value, decimal.Decimal) else value for key, value in properties.items()}
    # get the property hash and use that for saturation and lightness
    hue = hash(json.dumps(properties)) % 360
    saturation = 50
    lightness = 50
    return f'hsl({hue}, {saturation}%, {lightness}%)'

def get_features_geojson(m,geojson_data,layername,extra_columns,show_layers):

        # Define a tooltip format string
        tooltip_format = "<br>".join([f"<b>{alias}:</b> {{%s}}" % field for field, alias in zip(extra_columns, extra_columns)])

        if gdfType.values[0] == 'MultiPolygon':
            folium.GeoJson(
                geojson_data,
                name=layername,
                style_function=lambda feature: {
                    "fillColor": get_color(feature['properties']),
                    "color": "grey",      # Outline color
                    "weight": 1,          # Outline weight
                    "fillOpacity": 0.4,# Transparency of fill color
                    'show':show_layers.get(layername,True),
                },
                highlight_function=lambda feature: {
                    "fillColor": "rgba(255, 255, 255, 0.1)",   # Color for highlighted feature
                    "color": "grey",
                    "weight": 3,
                    "fillOpacity": 0.1
                },
                tooltip=folium.GeoJsonTooltip(fields=extra_columns, aliases=extra_columns)
            ).add_to(m)

        elif gdfType.values[0] == 'MultiLineString':
            line_attribute = extra_columns[1]
            # Create a colormap
            colormap = cm.linear.viridis.scale( round(gdf[line_attribute].min()),  round(gdf[line_attribute].max()))
            colormap.caption = extra_columns[1]
            m.add_child(colormap)
            def style_function(feature):
                # Get the normalized value for the current feature
                line_attribute = extra_columns[1]
                value = feature['properties'][line_attribute]
                color = colormap(value)
                return {
                    "color": color,
                    "weight": 3,
                    "opacity": 0.7
                }
            folium.GeoJson(
                geojson_data,
                name=layername,
                style_function=style_function,
                highlight_function=lambda feature: {
                    "color": "yellow",  # Highlighted line color
                    "weight": 5,        # Highlighted line weight
                    "opacity": 1        # Highlighted line opacity
                },
                tooltip=folium.GeoJsonTooltip(fields=extra_columns,
                                            aliases=extra_columns,
                                            localize=True,
                                            sticky=False,
                                            labels=True,)).add_to(m)

        else:
            print('Layer is neither MultiPolygon nor MultiLineString')
            return m

        return m

def getLineGeojson(m,table_name,extra_columns=[],show_layers=None):
    # get the connection url from the database
    db_connection_url = "postgresql://mtaa-wetu0:MtaaWetu***@postgresql-mtaa-wetu0.alwaysdata.net:5432/mtaa-wetu0_start"

    # create the connection engine
    db_conn = create_engine(db_connection_url)
    Session = sessionmaker(bind=db_conn)
    session = Session()

    try:
        # Join all the columns specified in *args into a comma-separated string
        columns_str = ', '.join(extra_columns)
        # get the connection url from the database
        sql = f'SELECT geom, {columns_str} FROM {table_name}'
        # create the geodataframe
        global gdf
        gdf = gpd.GeoDataFrame.from_postgis(sql, db_conn, geom_col='geom')
        # Ensure the GeoDataFrame is in the correct CRS (EPSG:4326)
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        #drop any null values
        gdf = gdf.dropna()
        # print(gdf.head())
        global gdfType
        gdfType = gdf.geometry.geometry.type
        global geojson_data
        geojson_data = gdf.to_json()
        if show_layers is None:
            show_layers = {}
        get_features_geojson(m=m,geojson_data=geojson_data,layername=table_name,extra_columns=extra_columns,show_layers=show_layers)

    except exc.SQLAlchemyError as e:
        print(f"Error occurred: {e}")
        session.rollback()
    finally:
        session.close()

    return m

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



def getGeoJsonPoints(hospital_group,m):
    # Construct the path to the file
    file_path = os.path.join(settings.BASE_DIR, 'points_cleaned.geojson')
    hospitals = gpd.read_file(file_path)
    columns_to_retain = ['osmid', 'geometry','name','amenity','check_date']
    hospitals = hospitals[columns_to_retain]
    star_rating = generate_star_rating(2)
    hospitals = hospitals.dropna()
    for idx, row in hospitals.iterrows():
        print(row['name'])
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            icon=folium.Icon(color='green'),
            tooltip=row['name'],
            popup= f"""
                    <div class="card border-0 shadow-md" style="width: 20rem;">
                        <div class="card-body">
                            <h5 class="card-title">{row['name']}</h5>
                            <p>Type: {row['amenity']}</p>
                            <p>Date: {row['check_date']}</p>
                            <div>Level of Satisfaction: {star_rating}</div>
                            <button class="open-dialogue" onclick="parent.postMessage({{ action: 'openCommentBox', data: '{row['name'].lower().title()}' }}, '*')" style="padding-left:0px; padding-top:2px;color:blue; background-color:transparent; border:none;outline:none;"> View and add comment </button>
                        </div>
                    </div>
                    """
        ).add_to(hospital_group)


        # Use get_or_create to check if the amenity exists and create it if it doesn't
        amenity, created = Amenities.objects.get_or_create(name=row['name'].title(),amenity_type=row['amenity'])
        if created:
            print(f"Amenity {row.name} created in the database.")
        else:
            print(f"Amenity {row.name} already exists in the database.")


    hospital_group.add_to(m)

def getRandomColor():
    color = color_values[random.randint(0,len(color_values))-1]
    return color

def getPointData(m,group,lat, lon, table_name, extra_columns=[]):
    hospital_group = group
    '''
    lat: string: latitude
    lon: string: longitude
    table_name: string: Database table name
    extra_columns: list: other attributes to be returned
    '''
    # Get the connection URL from the database
    db_connection_url = "postgresql://mtaa-wetu0:MtaaWetu***@postgresql-mtaa-wetu0.alwaysdata.net:5432/mtaa-wetu0_start"
    # Create the connection engine
    db_conn = create_engine(db_connection_url)
    # Join all the columns specified in extra_columns into a comma-separated string
    columns_str = ', '.join(extra_columns)
    # Set the table name
    tablename = f'{table_name}'
    # Get the connection URL from the database
    sql = f'SELECT {lat},{lon}, {columns_str} FROM {table_name}'
    columns = [lat, lon] + extra_columns
    # Create the DataFrame
    sql_query = pd.read_sql_query(sql, db_conn)
    df = pd.DataFrame(sql_query, columns=columns)
    # Drop any null values
    df = df.dropna()
    # Convert DataFrame to GeoDataFrame
    def df_to_gdf(df, lat_col, lon_col, crs="EPSG:21037"):
        # Create a geometry column from latitude and longitude columns
        geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
        # Create a GeoDataFrame
        geodf = gpd.GeoDataFrame(df, geometry=geometry)
        # Set the coordinate reference system (CRS)
        geodf.set_crs(crs, inplace=True)
        return geodf
    # Convert the DataFrame to a GeoDataFrame
    df = df_to_gdf(df, lat, lon)
    for index, row in df.iterrows():
        # Generate star rating HTML (assuming you have a function for this)
        star_rating = generate_star_rating(2)
        # Create popup HTML with an onclick event to open the comments box
        popup_html = f"""
        <div class="card border-0 shadow-md" style="width: 20rem;">
            <div class="card-body">
                <h5 class="card-title">{row['f_name']}</h5>
                <p>Location: {row['location']}</p>
                <p>Division: {row['division']}</p>
                <div>Level of Satisfaction: {star_rating}</div>
                <button class="open-dialogue" onclick="parent.postMessage({{ action: 'openCommentBox', data: '{row['f_name'].lower().title()}' }}, '*')" style="padding-left:0px; padding-top:2px;color:blue; background-color:transparent; border:none;outline:none;"> View and add comment </button>
            </div>
        </div>
        """
        # Create a Marker with the formatted popup
        folium.Marker(
            location=[row['geometry'].y, row['geometry'].x],
            tooltip=row['f_name'],
            popup=folium.Popup(popup_html, max_width=2650),
            icon=folium.Icon(color='green'),
        ).add_to(hospital_group)

    # # Add the feature group to the map
    # hospital_group.add_to(m)

    print("Markers added")
    return m

def getOverpassData(hospital_group,school_group,table_name):
    # Overpass API
    if table_name == 'schoolaccessindexwalk':
        amenity_var = 'school'
    elif table_name == 'nbihealthaccess':
        amenity_var = 'hospital'
    else:
        amenity_var = 'hospital'

    # Define parameters
    radius = 25000
    latitude = -1.2921
    longitude = 36.8219
    amenity_type = f"amenity={amenity_var}"

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
        # Check if elements are available
        if data['elements']:
            print('success')
        for i in data['elements']:
            # Generate star rating HTML
            star_rating = generate_star_rating(i['tags'].get('rating', 0))

            # Define the HTML for the popup using Bootstrap card
            popup_html = f"""
            <div class="card border-0 shadow-md" style="width: 20rem;">
            <div class="card-body">
                <h5 class="card-title">{i['tags'].get('name', 'no name')}</h5>
                <p class="card-text">{i['tags'].get('description', 'No description available')}</p>
                <div>Level of Satisfaction: {star_rating}</div>
                <button class="open-dialogue" onclick="parent.postMessage({{ action: 'openCommentBox', data: '{i['tags'].get('name', 'no name').lower().title()}' }}, '*')" style="padding-left:0px; padding-top:2px;color:blue; background-color:transparent; border:none;outline:none;"> View and add comment </button>
            </div>
            </div>
            """

            # Use get_or_create to check if the amenity exists and create it if it doesn't
            amenity, created = Amenities.objects.get_or_create(name=i['tags'].get('name', 'name').title(),amenity_type=amenity_var)
            # if created:
            #     print(f"Amenity {i['tags'].get('name')} created in the database.")
            # else:
            #     print(f"Amenity {i['tags'].get('name')} already exists in the database.")
            if amenity_var == 'hospital':
                marker_group = hospital_group
                # Create a Marker with the formatted popup
                folium.Marker(
                    location=[i['lat'], i['lon']],
                    tooltip=i['tags'].get('name', "No name"),
                    popup=folium.Popup(popup_html, max_width=2750),
                    icon=folium.Icon(color="red"),
                ).add_to(marker_group)
            elif amenity_var == 'school':
                marker_group = school_group
                # Create a Marker with the formatted popup
                folium.Marker(
                    location=[i['lat'], i['lon']],
                    tooltip=i['tags'].get('name', "No name"),
                    popup=folium.Popup(popup_html, max_width=2750),
                    icon=folium.Icon(color="red"),
                ).add_to(marker_group)


        else:
            print("No elements Available ")
    # Handle any errors
    else:
        print("Error:", response.status_code)



def create_chloropeth(m,hospital_group,school_group,table_name, legend_name, extra_columns=[]):
    '''
    table_name: string: Database table name
    legend_name: string: Name of the legend
    extra_columns: list: other attributes to be returned
    '''

    if table_name == 'nbihealthaccess':
        getPointData(m=m,group=hospital_group, lat='latitude', lon='longitude', table_name='nairobi_hospitals', extra_columns=['f_name', 'location', 'agency', 'division'])
        # getGeoJsonPoints(m=m,marker_group=marker_group)

    # Join all the columns specified in *args into a comma-separated string
    columns_str = ', '.join(extra_columns)
    # Set the table name
    tablename = f'{table_name}'
    # Get the connection url from the database
    db_connection_url = "postgresql://mtaa-wetu0:MtaaWetu***@postgresql-mtaa-wetu0.alwaysdata.net:5432/mtaa-wetu0_start"

    # Create the connection engine
    con = create_engine(db_connection_url)

    try:
        # Run the SQL query to postGIS
        sql = f'SELECT geom, {columns_str} FROM {table_name}'
        # Create the GeoDataFrame
        df = gpd.GeoDataFrame.from_postgis(sql, con)
    except Exception as e:
        print(f"Error with the Query: {e}")
        return 'error with the Query check the parameters and try again'

    # Drop any null values
    df = df.dropna()
    print(df.head())
    extra_columns = [col.strip() for col in extra_columns[1].split(',')]
    print(extra_columns)
    # Convert columns starting from the third column to float
    df[df.columns[2:3]] = df[df.columns[2:3]].astype(float)
    key_on = extra_columns[0]
    # Create the choropleth layer
    choropleth = folium.Choropleth(
        geo_data=df,  # Data to be used
        data= df.iloc[:, :3],  # Data to be used
        columns=['id', extra_columns[0]],  # Column with area names and numeric values
        key_on=f"feature.properties.id",  # Key to match GeoDataFrame with GeoJSON features
        fill_color=getRandomColor(),  # Color scheme for the map
        fill_opacity=0.4,  # Opacity of the fill color
        line_opacity=0.2,  # Opacity of the border lines
        legend_name=legend_name,  # Name of the legend
        name=table_name,
        bins=5,  # Number of bins for the scale
    ).add_to(m)

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(fields=extra_columns, aliases=extra_columns, localize=True)
    )

    if table_name in ['schoolaccessindexwalk','nbihealthaccess']:
        print("getting overpass")
        # if table_name == 'schoolaccessindexwalk':
        #     getOverpassData(hospital_group=hospital_group,school_group=school_group,table_name=table_name)
        if table_name == 'nbihealthaccess':
            getOverpassData(hospital_group=hospital_group,school_group=school_group,table_name=table_name)

    return m

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

    folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                    zoom_control = False,
                    zoom_start=12,
                    width='100%',
                    height="100%",
                    show=False,
                    name="Esri World Imagery",
                    attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community').add_to(m)

    marker_group = folium.FeatureGroup(name='Service buildings',show=False)

    # connect to the database
    # getPointData(m=m,marker_group=marker_group ,lat='latitude',lon='longitude',table_name='nairobi_hospitals',extra_columns=['f_name', 'location','agency','division'])
    # create_chloropeth(m=m,marker_group=marker_group,table_name="schoolaccessindexdrive",legend_name='school access Index',extra_columns=['id','schoolacce'])
    getLineGeojson(m,table_name='estates_nairobi',extra_columns=['name','shape_area'])
    getLayercontrol(m)
    folium.LayerControl().add_to(m)
    print("I am getting the layers! ")
    context = {
        'map': m._repr_html_(),
        # 'layer_options': layers_dict,
        'attribute_options': attribute_options,
    }

    return render(request,'base.html',context)





def getLayers(request):

    # Create individual FeatureGroups for hospitals and schools
    hospital_group = folium.FeatureGroup(name='Hospitals', show=False)
    school_group = folium.FeatureGroup(name='Schools', show=False)
    m = folium.Map(
                location = (-1.2921, 36.8219),
                zoom_control=False,
                zoom_start=12)

    folium.TileLayer(
        tiles=custom_tile_url,
        name=custom_tile_name,
        attr='CartoDB'
    ).add_to(m)


    folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                zoom_control = False,
                zoom_start=12,
                width='100%',
                height="100%",
                show=False,
                name="Esri World Imagery",
                attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community').add_to(m)

    # Add individual marker groups to the service buildings group
    if hospital_group:
        hospital_group.add_to(m)
    if school_group:
        school_group.add_to(m)



    # Ensure the 'estates_nairobi' layer is always loaded by default
    # show_layers = {'estates_nairobi': True}  # Change to False if it should be hidden by default
    # getLineGeojson(m, table_name='estates_nairobi', extra_columns=['name', 'shape_area'], show_layers=show_layers)


    if request.method == 'POST':
        # Process POST data
        data = json.loads(request.body)
        table_name = data.get('layerSelect')
        legend_name = table_name
        attribute = data.get('attributeSelect')
        print("initial table Name", table_name)
        table_name,attribute = filterLayers(table_name,attribute)

        if isinstance(attribute, list):
            attribute = ', '.join(attribute)
        print("atrribute: ", attribute)
        print("After filter table_name: ", table_name,attribute)

        if table_name == 'sdna_1500meters_2018' or table_name == 'sdna_1000meters_2018' or table_name == 'sdna_500meters_2018':
            print(table_name)
            getLineGeojson(m,table_name=table_name,extra_columns=['id',f'{attribute}'])
        elif table_name == 'ccn_zones':
            getLineGeojson(m,table_name=table_name,extra_columns=['zone_id_1',f'{attribute}'])
        else:
            create_chloropeth(m=m,hospital_group=hospital_group,school_group=school_group,table_name=table_name,legend_name=legend_name,extra_columns=['id',f'{attribute}'])

        getLayercontrol(m)
        folium.LayerControl().add_to(m)

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


def home(request):
    return render(request,'intro/intro.html')

@csrf_exempt
def get_marker_info(request):
    if request.method == 'POST':
        marker_name = request.POST.get('marker_name')
        map_html = request.POST.get('map_html')
        response_data = {'open':'true','name': marker_name,'map_html': map_html}
        return JsonResponse(response_data, safe=True)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



def getMarkerInfoFromModel(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        satisfaction = data.get('satisfaction')
        comment = data.get('comment')
        name = data.get('name')
        # print("name" + name, + "\n comment" + comment + "\n satisfaction"+ str(satisfaction))
        amenity = Amenities.objects.get(name=name)
        # Save the data to the database or perform any necessary actions
        # Example: MyModel.objects.create(satisfaction=satisfaction, comment=comment)

        s = Satisfaction.objects.create(amenity = amenity,comment=comment,satisfaction_range = satisfaction)
        s.save()

        return JsonResponse({'success': True})
    else:
        title = request.GET.get('title', None)
        if title:
            comments = Satisfaction.objects.filter(amenity__name=title).values_list('comment','date_posted')
            comments_list = list(comments)
        else:
            comments_list = []

        return JsonResponse({'success': True,'comments':comments_list})
def getResearch(request):
    papers = Research.objects.all()
    papers = list(papers.values())
    context = {
        'research':papers
    }
    return render(request, 'content/research.html', context=context)

def getResearchPaper(request, paper_name):
    paper = get_object_or_404(Research, title=paper_name)
    context = {
        'research':paper
    }
    return render(request, 'content/researchpaper.html',context=context)


def searchResearch(request):
    query = request.GET.get('q', '')
    if query:
        papers = Research.objects.filter(title__startswith=query).values('title', 'Author', 'source')
    else:
        papers = Research.objects.all().values('title', 'Author', 'source')
    return JsonResponse(list(papers), safe=False)
