import requests
import json
import os
from shutil import copyfile

OVERPASS_API = "https://overpass-api.de/api/interpreter"
OVERPASS_QUERY = """
[out:json][timeout:1800];
area["name"="Côte d'Ivoire"]->.searchArea;
(
  way["natural"="water"](area.searchArea);
  relation["natural"="water"](area.searchArea);
);
out geom tags;
"""

def fetch_osm_data():
    print("Extraction des données OSM...")
    response = requests.post(OVERPASS_API, data={'data': OVERPASS_QUERY})
    response.raise_for_status()
    return response.json()

def way_to_geojson_feature(way):
    coords = [[pt['lon'], pt['lat']] for pt in way['geometry']]
    # Fermer le polygone si besoin
    if coords and coords[0] != coords[-1]:
        coords.append(coords[0])
    props = {
        "name": way.get('tags', {}).get('name', ''),
        "type": "lac" if "lac" in way.get('tags', {}).get('name', '').lower() else 
                "lagune" if "lagune" in way.get('tags', {}).get('name', '').lower() else
                way.get('tags', {}).get('natural', ''),
        "surface": way.get('tags', {}).get('surface', ''),
        "description": way.get('tags', {}).get('description', '')
    }
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {
            "type": "Polygon",
            "coordinates": [coords]
        }
    }

def relation_to_geojson_feature(rel):
    multipolygons = []
    for member in rel.get('members', []):
        if member.get('geometry'):
            coords = [[pt['lon'], pt['lat']] for pt in member['geometry']]
            if coords and coords[0] != coords[-1]:
                coords.append(coords[0])
            multipolygons.append([coords])
    props = {
        "name": rel.get('tags', {}).get('name', ''),
        "type": "lac" if "lac" in rel.get('tags', {}).get('name', '').lower() else 
                "lagune" if "lagune" in rel.get('tags', {}).get('name', '').lower() else
                rel.get('tags', {}).get('natural', ''),
        "surface": rel.get('tags', {}).get('surface', ''),
        "description": rel.get('tags', {}).get('description', '')
    }
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": multipolygons
        }
    }

def main():
    osm_data = fetch_osm_data()
    features = []
    for el in osm_data.get('elements', []):
        if el['type'] == 'way' and el.get('geometry'):
            features.append(way_to_geojson_feature(el))
        elif el['type'] == 'relation' and el.get('members'):
            features.append(relation_to_geojson_feature(el))
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    output_path = "lacs_cotedivoire.geojson"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"Extraction terminée ! Fichier {output_path} généré avec {len(features)} plans d'eau.")

    # Copie automatique dans app/src/main/assets/
    assets_path = "app/src/main/assets/"
    os.makedirs(assets_path, exist_ok=True)
    copyfile(output_path, os.path.join(assets_path, output_path))
    print(f"Fichier copié dans {assets_path}")

if __name__ == "__main__":
    main()