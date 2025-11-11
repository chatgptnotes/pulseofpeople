# Production GeoJSON Data Guide for Tamil Nadu Map

## ✅ Current Status

**Implemented:**
- ✅ 12 major districts with improved boundaries (Chennai, Coimbatore, Madurai, Trichy, Salem, Tirunelveli, Vellore, Erode, Thanjavur, Dindigul, Kanyakumari, Villupuram)
- ✅ Real district-level GeoJSON file loaded into map
- ✅ Improved map centering (zoom 7.5)
- ✅ Click interaction enabled for drill-down

**What's Now Working:**
1. Click Tamil Nadu map → Districts appear with colors
2. Click district → View constituency level (mock data)
3. Click constituency → View polling booths
4. Breadcrumb navigation works
5. Sentiment legend displays

---

## 🎯 Next Steps for Production-Ready Data

### Option 1: DataMeet (Recommended - Free & Open Source)

**Download Tamil Nadu Boundaries:**

1. Visit: https://github.com/datameet/maps
2. Navigate to: `Districts/India/` folder
3. Download: `india_district.geojson` (all India districts including TN)

**Or get Tamil Nadu specifically:**

```bash
# Clone the repository
git clone https://github.com/datameet/maps.git
cd maps/Districts/India/

# Extract Tamil Nadu districts only
# Use jq or Python to filter features where properties.ST_NM === "Tamil Nadu"
```

**Files to get:**
- `tamil_nadu_districts.geojson` - District boundaries
- `tamil_nadu_assembly_constituencies.geojson` - AC boundaries

### Option 2: Election Commission of India (Most Accurate)

**Official Source:**
- URL: https://eci.gov.in/delimitation-and-polling-stations/
- Format: Shapefiles (.shp)
- Need to convert to GeoJSON

**Conversion Process:**

```bash
# Install GDAL
brew install gdal  # macOS
# or
sudo apt-get install gdal-bin  # Linux

# Convert Shapefile to GeoJSON
ogr2ogr -f GeoJSON \
  -t_srs EPSG:4326 \
  tamilnadu_constituencies.json \
  TN_AC_2024.shp

# Simplify for web (reduce file size)
npm install -g mapshaper
mapshaper tamilnadu_constituencies.json \
  -simplify 5% keep-shapes \
  -o tamilnadu_constituencies_simplified.json
```

### Option 3: OpenStreetMap (Community Data)

**Using Overpass API:**

```python
import requests
import json

# Query for Tamil Nadu districts
overpass_url = "http://overpass-api.de/api/interpreter"
query = """
[out:json];
(
  relation["boundary"="administrative"]["admin_level"="5"]["name:en"~".*Tamil Nadu.*"];
);
out geom;
"""

response = requests.post(overpass_url, data={'data': query})
data = response.json()

# Convert to GeoJSON
# Process and save
```

### Option 4: Survey of India (Official Government)

**Contact:**
- Website: https://surveyofindia.gov.in/
- May require formal request for administrative boundaries
- Most accurate and legally valid data

---

## 📁 File Structure for Production

Place downloaded files in:

```
src/data/geo/
├── tamilnadu-state.json              ✅ Done (placeholder)
├── tamilnadu-districts.json           ✅ Done (12 major districts)
├── tamilnadu-all-districts.json      ⚠️ Need (all 38 districts)
├── tamilnadu-constituencies.json     ⚠️ Need (234 ACs)
├── puducherry-districts.json         ⚠️ Need (4 districts)
├── puducherry-constituencies.json    ⚠️ Need (30 ACs)
└── README.md                         ✅ Done
```

---

## 🔧 Integration Steps

### 1. Download High-Resolution Data

**For Districts (38 total):**

```bash
# Download from DataMeet
wget https://raw.githubusercontent.com/datameet/maps/master/Districts/India/TamilNadu/tamilnadu_district.geojson

# Place in your project
mv tamilnadu_district.geojson src/data/geo/tamilnadu-all-districts.json
```

### 2. Download Constituency Data (234 ACs)

```bash
# From ECI or DataMeet
# Convert shapefiles if needed
ogr2ogr -f GeoJSON -t_srs EPSG:4326 \
  tamilnadu_constituencies.json \
  TN_AC.shp

# Simplify for web performance
mapshaper tamilnadu_constituencies.json \
  -simplify 5% keep-shapes \
  -o src/data/geo/tamilnadu-constituencies.json
```

### 3. Update Map Component

The component is already set up to use the files! Just replace:

```typescript
// src/components/maps/TamilNaduMap.tsx
// Already imports: tamilNaduDistrictsGeoJSON

// For constituencies, add:
import tamilNaduConstituenciesGeoJSON from '../../data/geo/tamilnadu-constituencies.json';

// Then in drillDownToConstituencies function, use:
setCurrentGeoJSON(tamilNaduConstituenciesGeoJSON);
```

---

## 🎨 Data Quality Checklist

When downloading GeoJSON, ensure:

✅ **Coordinate System:** EPSG:4326 (WGS84)
✅ **Simplification:** 5-10% (balance between quality & performance)
✅ **File Size:** < 2MB per file (use TopoJSON if larger)
✅ **Properties Include:**
   - District/constituency name
   - Code (TN01, TN02, etc.)
   - Population
   - Area in sq km

---

## 📊 Example GeoJSON Structure

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Chennai",
        "code": "TN03",
        "district_id": "TN03",
        "state": "Tamil Nadu",
        "population": 4646732,
        "area_sqkm": 426
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [80.15, 13.20],
          [80.28, 13.22],
          // ... more coordinates
        ]]
      }
    }
  ]
}
```

---

## 🚀 Quick Start with Real Data

### Fastest Way (5 minutes):

```bash
# 1. Clone DataMeet maps
git clone --depth=1 https://github.com/datameet/maps.git

# 2. Copy Tamil Nadu files
cp maps/Districts/Tamil\ Nadu/*.geojson src/data/geo/

# 3. Rename for consistency
cd src/data/geo/
mv tamil_nadu_district.geojson tamilnadu-all-districts.json
mv tamil_nadu_assembly.geojson tamilnadu-constituencies.json

# 4. Restart dev server
npm run dev
```

---

## 🔍 Data Validation

Test your GeoJSON files:

```bash
# Install geojsonhint
npm install -g @mapbox/geojsonhint

# Validate files
geojsonhint src/data/geo/tamilnadu-all-districts.json
geojsonhint src/data/geo/tamilnadu-constituencies.json
```

**Online Validators:**
- http://geojson.io - Visual editor
- https://geojsonlint.com - Quick validation

---

## 📈 Performance Optimization

### Convert to TopoJSON (60-80% smaller):

```bash
npm install -g topojson

# Convert GeoJSON to TopoJSON
geo2topo districts=src/data/geo/tamilnadu-all-districts.json \
  > src/data/geo/tamilnadu-districts.topojson

# Update component to use topojson-client
npm install topojson-client
```

```typescript
import * as topojson from 'topojson-client';
import topoData from '../../data/geo/tamilnadu-districts.topojson';

// Convert to GeoJSON in component
const geoData = topojson.feature(topoData, topoData.objects.districts);
```

---

## 🎯 Current Implementation Status

| Feature | Status | File |
|---------|--------|------|
| State boundary | ✅ Working | `tamilnadu-state.json` |
| District boundaries (12) | ✅ Working | `tamilnadu-districts.json` |
| All 38 districts | ⚠️ Partial | Need download |
| 234 constituencies | ❌ Mock | Need download |
| 30 Puducherry ACs | ❌ Mock | Need download |
| Polling booth coords | ✅ Sample | Need import |

---

## 📝 Recommended Action Plan

### Week 1:
1. Download DataMeet district GeoJSON ✅ (Already have 12)
2. Download all 38 districts from official source
3. Test district drill-down with real data

### Week 2:
4. Get ECI constituency shapefiles
5. Convert to GeoJSON
6. Import polling booth coordinates from CEO TN website

### Week 3:
7. Optimize file sizes with TopoJSON
8. Add district labels on map
9. Performance testing with real data

---

## 🔗 Useful Resources

- **DataMeet Maps:** https://github.com/datameet/maps
- **Election Commission:** https://eci.gov.in/
- **CEO Tamil Nadu:** https://www.elections.tn.gov.in/
- **QGIS (GIS Software):** https://qgis.org/
- **MapShaper (Simplify):** https://mapshaper.org/
- **GeoJSON.io:** http://geojson.io/

---

**Last Updated:** November 6, 2025
**Current Version:** Phase 1 - Districts implemented
**Next Phase:** Complete all 38 districts + constituencies
