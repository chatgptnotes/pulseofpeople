# Quick Start Guide - 5 Minutes to First Ward Upload

## Overview

This guide will get you from zero to your first ward and polling booth uploaded in just 5 minutes.

**What you'll accomplish:**
1. ✅ Set up your development environment
2. ✅ Create your first ward
3. ✅ Upload your first polling booth
4. ✅ View it on the interactive map

**Prerequisites:**
- Computer with internet connection
- Basic computer skills (no coding required for data entry)

**Time Required:** 5-10 minutes

---

## Step 1: Access the Platform (30 seconds)

### Option A: If you have login credentials

1. Open your web browser
2. Navigate to: `https://pulseofpeople.com` (or your deployment URL)
3. Click **Login**
4. Enter your credentials
5. Click **Sign In**

### Option B: Request access

1. Contact your administrator
2. Or sign up at `https://pulseofpeople.com/signup`
3. Wait for approval email

---

## Step 2: Verify Your Role (15 seconds)

After logging in, check your role in the top-right corner:

**Required Role:** Admin or Superadmin (to upload data)

**If you're a Viewer/Analyst:**
- You can view data but not upload
- Contact admin to upgrade your role

---

## Step 3: Upload Your First Ward (2 minutes)

### Quick Method: Single Ward via UI

1. **Navigate to Wards**
   - Click **Master Data** in sidebar
   - Click **Wards**

2. **Click "Add Ward" Button**
   - Top-right corner, blue button

3. **Fill in Ward Details:**
   ```
   Constituency: Select "Chennai Central" (or your constituency)
   Ward Name: Test Ward 1
   Ward Number: 1
   Ward Code: TN-AC-001-W-001
   Population: 25000
   Voter Count: 18500
   Total Booths: 5
   Urbanization: Urban
   Income Level: Medium
   ```

4. **Click "Save"**

5. **Success!** You should see a confirmation message

### Alternative: CSV Upload (for multiple wards)

**Skip to Step 4 if you created a single ward above**

1. **Download Template**
   - Click "Upload CSV" button
   - Click "Download Template"
   - Save `wards_template.csv`

2. **Fill in Template**
   Open in Excel/Google Sheets:
   ```csv
   constituency_code,ward_name,ward_number,ward_code,population,voter_count,total_booths,urbanization,income_level
   TN-AC-001,Test Ward 1,1,TN-AC-001-W-001,25000,18500,5,urban,medium
   TN-AC-001,Test Ward 2,2,TN-AC-001-W-002,22000,16200,4,urban,medium
   ```

3. **Upload CSV**
   - Click "Choose File"
   - Select your CSV
   - Click "Import"
   - Wait for validation
   - Click "Confirm Import"

---

## Step 4: Upload Your First Polling Booth (2 minutes)

### Quick Method: Single Booth via UI

1. **Navigate to Polling Booths**
   - Click **Master Data** → **Polling Booths**

2. **Click "Add Booth" Button**

3. **Fill in Booth Details:**
   ```
   Constituency: Chennai Central
   Ward: Test Ward 1 (the ward you just created)
   Booth Number: 001
   Booth Name: Government High School Test
   Address: 123 Test Street, Chennai
   Latitude: 13.0827
   Longitude: 80.2707
   Total Voters: 1500
   Male Voters: 750
   Female Voters: 750
   Accessible: Yes (check the box)
   Landmark: Near Test Landmark
   ```

4. **Click "Save"**

5. **Success!** Your first booth is created!

### Alternative: CSV Upload

1. **Download Template**
   - Download `booths_template.csv`

2. **Fill in Data:**
   ```csv
   constituency_code,ward_code,booth_number,booth_name,address,latitude,longitude,total_voters,male_voters,female_voters,accessible,landmark
   TN-AC-001,TN-AC-001-W-001,001,Government High School Test,"123 Test St, Chennai",13.0827,80.2707,1500,750,750,true,Near Test Landmark
   TN-AC-001,TN-AC-001-W-001,002,Primary School Test,"456 Test Rd, Chennai",13.0850,80.2720,1400,700,700,false,Opposite Park
   ```

3. **Upload and Import**
   - Same process as ward upload

---

## Step 5: View on Map (1 minute)

1. **Navigate to Maps**
   - Click **Maps** in sidebar
   - Or click **Interactive Map** button

2. **Find Your Data:**
   - Map should load showing Tamil Nadu
   - Click on **Chennai district**
   - Map zooms in
   - Click on **Chennai Central constituency**
   - You should see your ward boundary (if provided)

3. **See Your Booth:**
   - Zoom in further
   - Look for a **marker/pin** at coordinates (13.0827, 80.2707)
   - Click on the marker
   - A popup shows your booth details!

4. **Success!** You can now see your data on the map!

---

## Troubleshooting (if something goes wrong)

### "Constituency not found" error

**Problem:** The constituency code doesn't exist

**Solution:**
1. Go to **Master Data** → **Constituencies**
2. Check available constituencies
3. Use the exact code from the list
4. Or create the constituency first (Admin only)

### "Booth not showing on map"

**Problem:** GPS coordinates might be wrong or zoom level too high

**Solution:**
1. Verify latitude/longitude are correct
2. Zoom in closer (booths appear at ward/constituency level)
3. Check that booth is marked as "Active"
4. Refresh the page

### "Access Denied"

**Problem:** You don't have permission

**Solution:**
1. Check your role (top-right corner)
2. Contact admin to upgrade role
3. Ensure you're logged in

---

## Next Steps

Now that you've created your first ward and booth:

### Learn More
1. **Read the Full User Guide:** `USER_GUIDE_WARDS_BOOTHS.md`
2. **Understand CSV Format:** `CSV_FORMAT_GUIDE.md`
3. **Explore API:** `API_REFERENCE.md` (for developers)

### Import More Data

**For a single constituency (recommended next step):**

1. **Prepare your data:**
   - Collect official ward data (from Election Commission)
   - Get polling booth information
   - Find GPS coordinates (Google Maps)

2. **Create CSV files:**
   - One file for wards
   - One file for booths
   - Use templates provided

3. **Upload in batches:**
   - Upload wards first (all wards for one constituency)
   - Then upload booths (all booths for those wards)
   - Verify on map
   - Move to next constituency

**Best Practice Workflow:**

```
Day 1: Import 5 priority constituencies
  ├─ Chennai Central
  ├─ Chennai North
  ├─ Chennai South
  ├─ Coimbatore South
  └─ Madurai Central

Day 2: Verify and fix errors
  ├─ Check map display
  ├─ Verify voter counts
  └─ Fix any data issues

Day 3-7: Expand coverage
  ├─ Import remaining Chennai constituencies (11 more)
  ├─ Import Coimbatore (10 constituencies)
  └─ Continue with other districts
```

---

## Common Questions

**Q: How many wards should each constituency have?**

A: It varies. Urban constituencies may have 20-30 wards, rural constituencies may have 10-15. Check official data.

**Q: What if I don't have GPS coordinates for booths?**

A: You can:
1. Use Google Maps to find coordinates (right-click → "What's here?")
2. Upload without coordinates initially (booths won't show on map)
3. Add coordinates later via edit function

**Q: Can I update data after uploading?**

A: Yes! You can:
1. Edit individual wards/booths via UI
2. Re-upload CSV with same codes (system will update)
3. Bulk update via API (advanced)

**Q: How do I delete a ward?**

A:
1. Go to Master Data → Wards
2. Find the ward
3. Click Actions → Delete
4. Note: You must delete or reassign all booths first

**Q: What's the maximum file size for CSV upload?**

A: 50 MB (approximately 100,000 rows). For larger datasets, split into multiple files.

---

## Video Tutorial (Coming Soon)

Watch our 5-minute video tutorial:
- [Quick Start Video] (link to be added)

---

## Get Help

**Need assistance?**

1. **Documentation:**
   - Full User Guide: `USER_GUIDE_WARDS_BOOTHS.md`
   - CSV Format Guide: `CSV_FORMAT_GUIDE.md`
   - Database Schema: `DATABASE_SCHEMA.md`
   - API Reference: `API_REFERENCE.md`

2. **Support:**
   - Email: support@pulseofpeople.com
   - Phone: +91-XXX-XXX-XXXX
   - Hours: Mon-Fri, 9 AM - 6 PM IST

3. **Training:**
   - Schedule a demo: [Booking link]
   - Join webinar: [Webinar link]

---

## Summary Checklist

After completing this guide, you should have:

- ✅ Logged into the platform
- ✅ Created at least one ward
- ✅ Created at least one polling booth
- ✅ Viewed your data on the interactive map
- ✅ Understood the basic workflow
- ✅ Know where to find more help

**Congratulations!** You're now ready to upload electoral data at scale.

---

## Keyboard Shortcuts (Bonus)

Speed up your workflow:

| Shortcut | Action |
|----------|--------|
| `Ctrl + K` | Global search |
| `Ctrl + N` | New record (when in list view) |
| `Ctrl + S` | Save current form |
| `Esc` | Close modal/dialog |
| `Ctrl + M` | Open map view |

---

## Pro Tips

1. **Use Templates:** Always start with official CSV templates
2. **Test First:** Upload 10 rows, verify, then upload all
3. **Backup Data:** Export your data regularly
4. **Check Map:** Always verify booths appear correctly on map
5. **Use Filters:** Filter by constituency to find your data quickly
6. **GPS Precision:** Use 6-8 decimal places for coordinates
7. **Naming Convention:** Be consistent with ward/booth naming

---

## Ready to Scale?

Once you're comfortable with the basics:

1. **Set up bulk imports** (100+ wards at once)
2. **Integrate with APIs** (for automated updates)
3. **Add ward boundaries** (GeoJSON polygons)
4. **Enable real-time sync** (with field team)
5. **Configure alerts** (for data quality issues)

See `USER_GUIDE_WARDS_BOOTHS.md` for advanced features.

---

**Last Updated**: November 9, 2025
**Version**: 1.0
**For**: Pulse of People Platform

**Ready to start?** [Go to Step 1](#step-1-access-the-platform-30-seconds)
