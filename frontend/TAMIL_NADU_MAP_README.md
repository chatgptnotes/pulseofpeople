# Tamil Nadu Interactive Electoral Map

## 🗺️ Overview

A comprehensive, interactive electoral map of Tamil Nadu and Pondicherry with 4-level drill-down capability:

1. **State Level** - Overview of Tamil Nadu + Pondicherry
2. **District Level** - 38 districts with sentiment visualization
3. **Constituency Level** - 234 assembly constituencies (TN) + 30 (Puducherry)
4. **Polling Booth Level** - Individual polling stations with clustered markers

## ✨ Features

### Interactive Map Components
- **Choropleth Visualization** - Color-coded regions based on TVK sentiment scores
- **Smooth Animations** - Framer Motion powered transitions between drill-down levels
- **Click-to-Drill** - Click any region to zoom in and explore details
- **Hover Tooltips** - Quick stats on hover
- **Breadcrumb Navigation** - Easy navigation back through levels
- **Polling Booth Markers** - Clustered markers for efficient booth visualization

### Sentiment Analysis
- **Real-time Sentiment Scores** - Positive, Neutral, Negative percentages
- **Color-Coded Intensity** - 6-level gradient from strong positive to strong negative
- **Confidence Scores** - Data reliability indicators
- **Historical Tracking** - Last updated timestamps

### Data Visualization
- **Interactive Popups** - Detailed constituency information
- **Statistics Dashboard** - Total voters, polling booths, sentiment breakdown
- **Color Legend** - Easy-to-understand sentiment scale guide
- **Export Capabilities** - Data export functionality (planned)

## 📁 Project Structure

```
src/
├── components/maps/
│   ├── TamilNaduMap.tsx              # Main orchestrator component
│   ├── LeafletChoropleth.tsx         # Base map with choropleth layers
│   ├── DrillDownControls.tsx         # Breadcrumb navigation
│   ├── SentimentLegend.tsx           # Color scale legend
│   ├── ConstituencyPopup.tsx         # Information popup modal
│   ├── PollingBoothMarkers.tsx       # Clustered booth markers
│   └── index.ts                      # Component exports
│
├── pages/
│   └── TamilNaduMapDashboard.tsx     # Full-page map dashboard
│
├── data/
│   ├── tamilnadu-data.ts             # District & constituency data
│   ├── polling-booths-sample.ts      # Sample polling booth data
│   └── geo/
│       ├── tamilnadu-state.json      # State boundary GeoJSON
│       └── README.md                 # Instructions for real boundary data
│
└── types/
    └── geography.ts                  # TypeScript type definitions
```

## 🚀 Getting Started

### Prerequisites

```bash
Node.js >= 18.0.0
npm >= 9.0.0
```

### Installation

```bash
# Install dependencies (if not already installed)
npm install

# Start development server
npm run dev
```

### Access the Map

1. Navigate to: `http://localhost:5173`
2. Login (or use demo mode)
3. Go to: **Navigation > Tamil Nadu Map**
4. Or directly: `http://localhost:5173/tamil-nadu-map`

## 📊 Data Structure

### Assembly Constituencies (264 total)

```typescript
interface AssemblyConstituency {
  code: string;                    // e.g., "TN001"
  name: string;                    // e.g., "Gummidipoondi"
  districtCode: string;            // e.g., "TN03"
  type: 'General' | 'SC' | 'ST';  // Reservation category
  center: { lat: number; lng: number };
  totalVoters: number;
  pollingBooths: number;
  sentiment?: SentimentScore;
  parliamentaryConstituency?: string;
}
```

### Polling Booths

```typescript
interface PollingBooth {
  id: string;                      // e.g., "TN015-001"
  name: string;                    // Booth name
  boothNumber: string;             // e.g., "001"
  constituencyCode: string;
  location: { lat: number; lng: number };
  totalVoters: number;
  address: string;
  sentiment?: SentimentScore;
}
```

### Sentiment Scores

```typescript
interface SentimentScore {
  positive: number;    // 0-100
  neutral: number;     // 0-100
  negative: number;    // 0-100
  overall: 'positive' | 'neutral' | 'negative';
  confidence: number;  // 0-1
  lastUpdated: string; // ISO date
}
```

## 🎨 Color Scheme

### Sentiment Colors

| Sentiment | Color | Range | Description |
|-----------|-------|-------|-------------|
| Strong Positive | `#15803d` (green-700) | 70-100% | Very strong support |
| Positive | `#22c55e` (green-500) | 50-69% | Positive sentiment |
| Neutral | `#eab308` (yellow-500) | 40-49% | Undecided/Mixed |
| Negative | `#ef4444` (red-500) | 30-39% | Negative sentiment |
| Strong Negative | `#991b1b` (red-800) | 0-29% | Very low support |
| No Data | `#9ca3af` (gray-400) | N/A | No data available |

## 🔧 Technical Stack

### Core Technologies
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Leaflet** - Interactive mapping library
- **React-Leaflet** - React wrapper for Leaflet
- **Framer Motion** - Smooth animations
- **Tailwind CSS** - Styling
- **Material-UI Icons** - Icon library

### Data Visualization
- **GeoJSON** - Geographic boundary data format
- **Choropleth Maps** - Sentiment-based coloring
- **Marker Clustering** - Efficient booth visualization

## 📍 Real GeoJSON Data

### Current Status
The map uses **simplified placeholder** GeoJSON data for demonstration. For production deployment, replace with high-resolution boundary data.

### Where to Get Real Data

1. **DataMeet India Maps** (Recommended)
   - URL: http://projects.datameet.org/maps/
   - GitHub: https://github.com/datameet/maps
   - License: CC BY 4.0 (Open Data)

2. **Election Commission of India**
   - URL: https://eci.gov.in/
   - Format: Shapefiles (convert to GeoJSON)
   - Most accurate official data

3. **Convert Shapefiles to GeoJSON**
   ```bash
   # Install GDAL
   brew install gdal  # macOS

   # Convert
   ogr2ogr -f GeoJSON -t_srs EPSG:4326 output.json input.shp

   # Simplify (optional, for performance)
   mapshaper input.json -simplify 10% -o output-simplified.json
   ```

### Required GeoJSON Files

Place these in `src/data/geo/`:

- `tamilnadu-state.json` - State outline ✅ (placeholder exists)
- `tamilnadu-districts.json` - 38 district boundaries ⚠️
- `tamilnadu-constituencies.json` - 234 AC boundaries ⚠️
- `puducherry-districts.json` - 4 district boundaries ⚠️
- `puducherry-constituencies.json` - 30 AC boundaries ⚠️

## 🎯 Usage Examples

### Basic Map Display

```tsx
import { TamilNaduMap } from '../components/maps';

function MyPage() {
  return <TamilNaduMap height="700px" />;
}
```

### With Custom Initial View

```tsx
<TamilNaduMap
  height="800px"
  initialZoom={8}
/>
```

### Full Dashboard Integration

```tsx
import TamilNaduMapDashboard from '../pages/TamilNaduMapDashboard';

// Already integrated in routing at /tamil-nadu-map
```

## 🔄 Drill-Down Flow

```
┌─────────────────────────────────────────┐
│  State View                             │
│  - Tamil Nadu + Pondicherry overview   │
│  - Overall sentiment statistics        │
│  - Click on state to view districts    │
└──────────────┬──────────────────────────┘
               │ Click
               ▼
┌─────────────────────────────────────────┐
│  District View                          │
│  - 38 districts color-coded            │
│  - Hover for quick stats               │
│  - Click district to drill down        │
└──────────────┬──────────────────────────┘
               │ Click
               ▼
┌─────────────────────────────────────────┐
│  Constituency View                      │
│  - 234 assembly constituencies         │
│  - Detailed sentiment breakdown        │
│  - Click constituency for booths       │
└──────────────┬──────────────────────────┘
               │ Click
               ▼
┌─────────────────────────────────────────┐
│  Polling Booth View                     │
│  - Individual booth markers            │
│  - Clustered for performance           │
│  - Click booth for details             │
└─────────────────────────────────────────┘
```

## 🎬 Animation Features

### Transitions
- **Fly-to Animation** - Smooth zoom transitions (1.2s duration)
- **Fade In/Out** - Layer transitions with opacity changes
- **Scale Animation** - Popup modals with spring physics
- **Stagger Effect** - Sequential breadcrumb animations

### Performance Optimizations
- Lazy loading of deeper drill-down levels
- Marker clustering for booth views
- Simplified polygon rendering
- Debounced hover events

## 📈 Data Integration

### Mock Data (Current)
- Sample constituencies with generated sentiment scores
- Mock polling booth locations
- Placeholder district boundaries

### Production Integration (Recommended)

```typescript
// Fetch real-time sentiment data
const fetchSentiment = async (constituencyCode: string) => {
  const response = await fetch(`/api/sentiment/${constituencyCode}`);
  return response.json();
};

// Fetch polling booth data
const fetchBooths = async (constituencyCode: string) => {
  const response = await fetch(`/api/booths/${constituencyCode}`);
  return response.json();
};
```

## 🐛 Troubleshooting

### Map not displaying?
1. Check Leaflet CSS is loaded
2. Ensure GeoJSON data is valid
3. Check browser console for errors
4. Verify coordinates are in EPSG:4326 format

### Markers not showing?
1. Check polling booth data has valid lat/lng
2. Ensure map instance is initialized
3. Verify drill-down level is 'booth'

### Slow performance?
1. Use TopoJSON instead of GeoJSON (60% smaller)
2. Simplify polygon boundaries
3. Enable marker clustering
4. Lazy load drill-down data

## 📝 Todo / Future Enhancements

- [ ] Integrate real Election Commission boundary data
- [ ] Add heatmap overlay for density visualization
- [ ] Implement time-series sentiment trends
- [ ] Add demographic filters (age, gender, etc.)
- [ ] Export map as image/PDF
- [ ] Real-time updates via WebSocket
- [ ] Mobile-optimized touch gestures
- [ ] Multi-language support (Tamil, English)
- [ ] Historical election results overlay
- [ ] Campaign event markers
- [ ] Voter turnout predictions

## 🤝 Contributing

### Adding New Districts
1. Add district data to `src/data/tamilnadu-data.ts`
2. Create GeoJSON boundary file
3. Update `allDistricts` object
4. Test drill-down functionality

### Adding New Constituencies
1. Add to `assemblyConstituencies` object
2. Link to parent district via `districtCode`
3. Provide center coordinates
4. Add sentiment data (or mock)

## 📄 License

This project is part of the Pulse of People platform.
Built for TVK (Thamizhaga Vettri Kazhagam) party - Led by Vijay.

## 🙏 Credits

- **DataMeet** - India maps and open data
- **Leaflet** - Open-source mapping library
- **OpenStreetMap** - Map tiles and data
- **Election Commission of India** - Official electoral data

---

**Last Updated:** November 6, 2025
**Version:** 1.0.0
**Built for:** TVK - Tamil Nadu Electoral Analysis
