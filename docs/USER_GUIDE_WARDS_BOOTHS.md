# User Guide: Wards and Polling Booths Management

## Table of Contents
1. [Introduction](#introduction)
2. [How to Upload Wards](#how-to-upload-wards)
3. [How to Upload Polling Booths](#how-to-upload-polling-booths)
4. [Using the Interactive Map](#using-the-interactive-map)
5. [Search and Filter](#search-and-filter)
6. [Export Data](#export-data)
7. [Common Issues and Solutions](#common-issues-and-solutions)
8. [FAQ](#faq)

---

## Introduction

The Pulse of People platform allows you to manage electoral data at the ward and polling booth level. This guide will walk you through:

- Uploading ward data via CSV files
- Uploading polling booth information
- Visualizing data on interactive maps
- Searching and filtering electoral data
- Exporting data for analysis

**User Roles:**
- **Admin/Superadmin**: Full upload and management access
- **Manager**: Can view and manage assigned areas
- **Analyst**: Can view and export data
- **Viewer**: Read-only access

---

## How to Upload Wards

### Step 1: Prepare Your CSV File

Download the ward template CSV file or create one with the following columns:

```csv
constituency_code,ward_name,ward_number,ward_code,population,voter_count,total_booths,urbanization,income_level
```

**Example:**
```csv
constituency_code,ward_name,ward_number,ward_code,population,voter_count,total_booths,urbanization,income_level
TN-AC-001,Anna Nagar Ward 1,1,TN-AC-001-W-001,25000,18500,12,urban,medium
TN-AC-001,Anna Nagar Ward 2,2,TN-AC-001-W-002,22000,16200,10,urban,medium
TN-AC-002,Kilpauk Ward 1,1,TN-AC-002-W-001,30000,22000,15,urban,high
```

**Important Notes:**
- `constituency_code` must match existing constituencies in the system
- `ward_code` must be unique across the entire system
- `ward_number` is the sequential number within the constituency
- `urbanization` options: `urban`, `semi-urban`, `rural`
- `income_level` options: `low`, `medium`, `high`

### Step 2: Access the Upload Interface

1. **Login** to your admin dashboard
2. Navigate to **Master Data** → **Wards**
3. Click the **Upload CSV** button (top-right corner)

![Upload Wards Button](../assets/screenshots/upload-wards-button.png)

### Step 3: Upload the CSV File

1. Click **Choose File** or drag-and-drop your CSV file
2. The system will validate your file automatically
3. Review the **validation summary**:
   - ✅ Valid rows: Will be imported
   - ⚠️ Warnings: Review before importing
   - ❌ Errors: Must fix before importing

### Step 4: Review and Confirm

1. Check the **preview table** showing the first 10 rows
2. Review any **warnings or errors**:
   - Missing constituency codes
   - Duplicate ward codes
   - Invalid data formats
3. Click **Import Data** to proceed

### Step 5: Monitor Import Progress

- A progress bar will show import status
- **Success**: You'll see a confirmation message with count of imported wards
- **Partial Success**: Some rows imported, others failed (download error report)
- **Failure**: Fix errors and try again

### Step 6: Verify Uploaded Data

1. Go to **Master Data** → **Wards**
2. Filter by constituency to view newly uploaded wards
3. Check the map view to see ward locations

---

## How to Upload Polling Booths

### Step 1: Prepare Your CSV File

Download the polling booth template CSV file or create one with these columns:

```csv
constituency_code,ward_code,booth_number,booth_name,address,latitude,longitude,total_voters,male_voters,female_voters,accessible,landmark
```

**Example:**
```csv
constituency_code,ward_code,booth_number,booth_name,address,latitude,longitude,total_voters,male_voters,female_voters,accessible,landmark
TN-AC-001,TN-AC-001-W-001,001,Government High School Anna Nagar,"123 Main St, Anna Nagar",13.0827,80.2707,1500,750,750,true,Near Anna Nagar Tower
TN-AC-001,TN-AC-001-W-001,002,Corporation Primary School,"456 Park Rd, Anna Nagar",13.0850,80.2720,1400,700,700,false,Opposite Park
TN-AC-001,TN-AC-001-W-002,003,Community Hall,"789 Lake View, Anna Nagar",13.0890,80.2750,1600,800,800,true,Next to Lake
```

**Important Notes:**
- Both `constituency_code` and `ward_code` must exist in the system
- `booth_number` must be unique within the constituency
- `latitude` and `longitude` are required for map display
- `accessible` must be `true` or `false` (wheelchair accessibility)
- `male_voters + female_voters` should equal `total_voters`

### Step 2: Access the Upload Interface

1. Navigate to **Master Data** → **Polling Booths**
2. Click **Upload CSV** button

### Step 3: Upload and Validate

1. **Choose your CSV file**
2. System validates:
   - ✅ Constituency codes exist
   - ✅ Ward codes exist
   - ✅ GPS coordinates are valid (within India)
   - ✅ Voter counts add up correctly
   - ✅ No duplicate booth numbers

### Step 4: Review Validation Results

**Common validation messages:**

| Message | Meaning | Action |
|---------|---------|--------|
| "Constituency not found" | Invalid constituency code | Check code against master list |
| "Ward not found" | Invalid ward code | Ensure wards are uploaded first |
| "Invalid GPS coordinates" | Lat/long out of range | Verify coordinates |
| "Voter count mismatch" | Male + Female ≠ Total | Fix the calculation |
| "Duplicate booth number" | Booth already exists | Use unique booth numbers |

### Step 5: Import Data

1. Fix any errors in your CSV
2. Re-upload if needed
3. Click **Import Data**
4. Monitor progress bar

### Step 6: Verify on Map

1. Go to **Maps** → **Polling Booths**
2. Select your constituency
3. Zoom into wards to see booth markers
4. Click on a booth marker to see details

---

## Using the Interactive Map

### Map Navigation

**Zoom Levels:**
- **State Level**: See all districts
- **District Level**: See all constituencies
- **Constituency Level**: See all wards
- **Ward Level**: See all polling booths

**Controls:**
- **Zoom In/Out**: Use `+/-` buttons or mouse wheel
- **Pan**: Click and drag the map
- **Reset View**: Click home button to return to state view

### Drill-Down Navigation

1. **Start at State Level** (Tamil Nadu/Puducherry)
2. **Click on a District** → Map zooms to district boundaries
3. **Click on a Constituency** → Map zooms to show wards
4. **Click on a Ward** → Map shows all polling booths

### Booth Details

Click on any booth marker to see:
- Booth name and number
- Full address
- Total voters (male/female breakdown)
- Accessibility status
- Nearby landmark
- GPS coordinates

### Heatmap View

**Sentiment Heatmap:**
1. Toggle **Heatmap View** button
2. See color-coded sentiment:
   - 🟢 Green: Positive sentiment (60-100%)
   - 🟡 Yellow: Neutral sentiment (40-60%)
   - 🔴 Red: Negative sentiment (0-40%)

**Voter Density Heatmap:**
1. Select **Density** from dropdown
2. See concentration of voters:
   - Dark blue: High concentration
   - Light blue: Medium concentration
   - White: Low concentration

---

## Search and Filter

### Global Search

1. Click the **search bar** at the top
2. Type to search for:
   - Ward name (e.g., "Anna Nagar Ward 1")
   - Booth name (e.g., "Government High School")
   - Booth number (e.g., "001")
   - Address (e.g., "Main Street")

3. Results show instantly as you type
4. Click a result to jump to that location on the map

### Advanced Filters

**Filter Panel** (left sidebar):

**By Geography:**
- State: Tamil Nadu / Puducherry
- District: Select from dropdown
- Constituency: Select from dropdown
- Ward: Select from dropdown

**By Attributes:**
- Urbanization: Urban / Semi-urban / Rural
- Income Level: Low / Medium / High
- Accessibility: Accessible only / All booths
- Voter Count: Min/Max range slider

**By Activity:**
- Booths with feedback: Show only booths with citizen feedback
- Booths with reports: Show only booths with field reports
- Recent activity: Last 7/30/90 days

**Apply Filters:**
1. Select your filter criteria
2. Click **Apply**
3. Map updates to show matching wards/booths
4. Results count shown at bottom

**Clear Filters:**
- Click **Clear All** to reset filters

### Saved Searches

**Save a Filter:**
1. Apply your desired filters
2. Click **Save Search**
3. Give it a name (e.g., "Urban High-Income Wards")
4. Click **Save**

**Load a Saved Search:**
1. Click **Saved Searches** dropdown
2. Select your saved search
3. Filters apply automatically

---

## Export Data

### Export Wards

1. Go to **Master Data** → **Wards**
2. Apply any filters (optional)
3. Click **Export** button
4. Choose format:
   - **CSV**: For Excel/spreadsheets
   - **JSON**: For developers
   - **PDF**: For reports

**CSV Export includes:**
- All ward details
- Constituency information
- Voter statistics
- Demographics

### Export Polling Booths

1. Go to **Master Data** → **Polling Booths**
2. Apply filters (optional)
3. Click **Export**
4. Select format

**CSV Export includes:**
- Booth number and name
- Address and GPS coordinates
- Voter counts (total, male, female, transgender)
- Accessibility status
- Ward and constituency information

### Export Map Data

**From Map View:**
1. Navigate to desired area
2. Click **Export** (top-right)
3. Choose **Visible Area** or **Selected Items**
4. Select format:
   - **GeoJSON**: For GIS software
   - **KML**: For Google Earth
   - **CSV**: For spreadsheets

**What's included:**
- Geographic boundaries (wards)
- Point locations (booths)
- All attribute data
- Sentiment scores (if available)

### Schedule Reports

**Automated Exports:**
1. Go to **Settings** → **Scheduled Reports**
2. Click **Create New Report**
3. Configure:
   - Report type: Wards / Booths / Combined
   - Frequency: Daily / Weekly / Monthly
   - Format: CSV / PDF / Excel
   - Email recipients
4. Click **Save**

Reports will be emailed automatically.

---

## Common Issues and Solutions

### Upload Issues

**Issue: "File format not recognized"**
- **Solution**: Ensure file is saved as `.csv` (not `.xlsx` or `.txt`)
- Use UTF-8 encoding
- Check for hidden characters

**Issue: "Constituency not found"**
- **Solution**:
  - Verify constituency code matches exactly (case-sensitive)
  - Check that constituency exists: Go to Master Data → Constituencies
  - Download the official constituency list

**Issue: "Duplicate ward code"**
- **Solution**:
  - Ward codes must be unique across the entire system
  - Use format: `{STATE}-AC-{CONSTITUENCY_NUM}-W-{WARD_NUM}`
  - Example: `TN-AC-001-W-001`

**Issue: "Invalid GPS coordinates"**
- **Solution**:
  - Latitude must be between 8° and 37° (India range)
  - Longitude must be between 68° and 97° (India range)
  - Use decimal format (e.g., `13.0827`, not `13°04'58"`)
  - Don't include degree symbols

**Issue: "Voter count mismatch"**
- **Solution**:
  - Ensure `male_voters + female_voters + transgender_voters = total_voters`
  - Use 0 for transgender_voters if not applicable
  - Double-check your calculations

### Map Display Issues

**Issue: Booths not showing on map**
- **Solution**:
  - Verify GPS coordinates are correct
  - Zoom in closer (booths appear at ward level)
  - Check filters aren't hiding booths
  - Clear browser cache and reload

**Issue: Ward boundaries not visible**
- **Solution**:
  - Ward boundaries require GeoJSON data
  - Upload ward boundaries separately (Admin → Upload Boundaries)
  - Contact admin if boundaries are missing

**Issue: Map is slow/laggy**
- **Solution**:
  - Filter to smaller area
  - Disable heatmap view
  - Close other browser tabs
  - Use Chrome/Firefox for best performance

### Search Issues

**Issue: Search returns no results**
- **Solution**:
  - Check spelling
  - Try partial matches (e.g., "Anna" instead of "Anna Nagar Ward 1")
  - Search is case-insensitive
  - Clear filters that might be excluding results

**Issue: Wrong booth appears in search**
- **Solution**:
  - Use booth number for exact match
  - Include ward or constituency name
  - Example: "Booth 001 Anna Nagar"

### Export Issues

**Issue: Export file is empty**
- **Solution**:
  - Check that you have data in the filtered view
  - Clear filters and try again
  - Check browser's download folder

**Issue: CSV file doesn't open in Excel**
- **Solution**:
  - Right-click file → Open with → Excel
  - Or import CSV in Excel: Data → From Text/CSV
  - Ensure UTF-8 encoding

---

## FAQ

### General Questions

**Q: How many wards can I upload at once?**
A: You can upload up to 10,000 rows in a single CSV file. For larger datasets, split into multiple files.

**Q: Can I update existing wards?**
A: Yes. Upload a CSV with the same `ward_code`. The system will update existing records.

**Q: How do I delete a ward?**
A: Go to Master Data → Wards, find the ward, click Actions → Delete. Note: You cannot delete wards that have polling booths.

**Q: What happens to booths when I delete a ward?**
A: You must delete or reassign all booths first. The system prevents deleting wards with associated booths.

### Data Questions

**Q: Where can I get official ward/booth data?**
A:
- Tamil Nadu CEO Office: https://ceotnelection.gov.in
- Puducherry CEO Office: https://ceopuducherry.py.gov.in
- Election Commission of India: https://eci.gov.in

**Q: How often should I update ward data?**
A: Update when:
- Electoral boundaries change
- New census data is available
- Booth locations are relocated
- Voter counts are updated

**Q: Can I import partial data?**
A: Yes. You can upload wards/booths incrementally. Start with priority constituencies and expand coverage.

**Q: What if I don't have GPS coordinates?**
A:
- Use Google Maps to find coordinates
- Right-click location → "What's here?"
- Or use geocoding service (contact support)

### Permission Questions

**Q: Who can upload ward/booth data?**
A: Only Admin and Superadmin roles. Managers can view but not upload.

**Q: Can I restrict data access by constituency?**
A: Yes. Admins can assign users to specific constituencies. Users only see data for their assigned areas.

**Q: How do I give someone upload access?**
A: Go to Settings → Users → Edit User → Change Role to "Admin"

### Technical Questions

**Q: What file size limit for CSV uploads?**
A: Maximum 50 MB per file (approximately 100,000 rows).

**Q: Can I automate uploads via API?**
A: Yes. See API_REFERENCE.md for details on the `/api/wards/bulk-upload/` endpoint.

**Q: How do I backup my data?**
A: Go to Settings → Backup & Export → Create Backup. Downloads all wards and booths as ZIP file.

**Q: Is my data secure?**
A: Yes. All data is encrypted at rest and in transit. Role-based access control ensures only authorized users can view/edit data.

### Troubleshooting

**Q: Upload stuck at "Processing..."**
A:
- Wait up to 5 minutes for large files
- If still stuck, refresh page and try again
- Check browser console for errors (F12)
- Contact support if problem persists

**Q: Map not loading**
A:
- Check internet connection
- Verify Mapbox token is configured (Admin only)
- Try different browser
- Clear cache: Ctrl+Shift+Delete

**Q: Export taking too long**
A:
- Apply filters to reduce data size
- Export in smaller chunks
- Use scheduled reports for large exports

**Q: GPS coordinates appear wrong on map**
A:
- Verify lat/long aren't swapped
- Check decimal precision (6-8 digits)
- Ensure coordinates are in decimal degrees, not DMS

### Best Practices

**Q: What's the best workflow for data entry?**
A:
1. Import constituencies first (if not already present)
2. Import all wards for a constituency
3. Import polling booths for those wards
4. Verify on map
5. Add boundaries (GeoJSON) if available

**Q: How do I handle data corrections?**
A:
1. Download current data (Export → CSV)
2. Make corrections in Excel
3. Re-upload corrected CSV
4. System updates existing records

**Q: Should I upload ward boundaries?**
A: Yes, if available. Boundaries enable:
- Better map visualization
- Spatial analysis
- Heatmap accuracy
- Area calculations

**Q: How do I organize booth numbers?**
A: Use a consistent format:
- Sequential: 001, 002, 003...
- By ward: W1-B001, W1-B002, W2-B001...
- Official EC numbering (recommended)

---

## Additional Resources

- **Video Tutorials**: [Link to video guides]
- **CSV Templates**: Available in the Upload interface
- **API Documentation**: See `API_REFERENCE.md`
- **Technical Support**: support@pulseofpeople.com
- **Community Forum**: [Link to forum]

---

## Need Help?

**Technical Support:**
- Email: support@pulseofpeople.com
- Phone: +91-XXX-XXX-XXXX
- Hours: Mon-Fri, 9 AM - 6 PM IST

**Training:**
- Schedule a demo: [Link to booking page]
- Watch tutorials: [Link to videos]
- Download PDF guides: [Link to resources]

---

**Last Updated**: November 9, 2025
**Version**: 1.0
**For**: Pulse of People Platform
