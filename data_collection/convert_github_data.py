#!/usr/bin/env python3
"""
GitHub Electoral Data Converter
Downloads and converts poll station metadata from GitHub to Pulse of People format

Source: https://github.com/in-rolls/poll-station-metadata
Dataset: 989K polling stations across India (2018-2019 data)
Output: CSV files ready for upload to Wards & Booths system
"""

import os
import sys
import csv
import subprocess
from pathlib import Path
from datetime import datetime
import re

# Configuration
GITHUB_REPO = "https://github.com/in-rolls/poll-station-metadata.git"
REPO_DIR = Path("github_data/poll-station-metadata")
ARCHIVE_FILE = "poll_station_metadata_all.7z"
EXTRACTED_CSV = "poll_station_metadata_all.csv"
OUTPUT_DIR = Path("converted_csvs")

# State/UT filters
TARGET_STATES = ["Tamil Nadu", "Puducherry"]

# Statistics
stats = {
    "total_records": 0,
    "tn_records": 0,
    "puducherry_records": 0,
    "wards_created": 0,
    "booths_created": 0,
    "skipped_invalid": 0,
    "duplicates_removed": 0,
}

def print_banner():
    """Print script banner"""
    print("=" * 80)
    print(" 🗳️  GitHub Electoral Data Converter - Pulse of People")
    print("=" * 80)
    print(f" Source: in-rolls/poll-station-metadata")
    print(f" Target: Tamil Nadu + Puducherry")
    print(f" Expected: ~20,000-25,000 polling booths")
    print("=" * 80)
    print()

def check_dependencies():
    """Check if required tools are installed"""
    print("📋 Checking dependencies...")

    # Check git
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("  ✅ git installed")
    except:
        print("  ❌ git not found. Install: brew install git")
        return False

    # Check 7z
    try:
        subprocess.run(["7z"], capture_output=True)
        print("  ✅ 7z installed")
    except:
        print("  ❌ 7z not found. Install: brew install p7zip")
        return False

    print()
    return True

def clone_repository():
    """Clone GitHub repository"""
    print("📥 Step 1: Cloning GitHub repository...")

    if REPO_DIR.exists():
        print(f"  ⏭️  Repository already exists at: {REPO_DIR}")
        return True

    try:
        REPO_DIR.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", GITHUB_REPO, str(REPO_DIR)],
            check=True,
            capture_output=True
        )
        print(f"  ✅ Cloned to: {REPO_DIR}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Clone failed: {e}")
        return False

def extract_archive():
    """Extract 7z archive"""
    print(f"\n📦 Step 2: Extracting archive...")

    archive_path = REPO_DIR / ARCHIVE_FILE
    csv_path = REPO_DIR / EXTRACTED_CSV

    if csv_path.exists():
        print(f"  ⏭️  CSV already extracted: {csv_path}")
        return True

    if not archive_path.exists():
        print(f"  ❌ Archive not found: {archive_path}")
        return False

    try:
        print(f"  📦 Extracting {ARCHIVE_FILE} (this may take 2-3 minutes)...")
        subprocess.run(
            ["7z", "x", str(archive_path), f"-o{REPO_DIR}"],
            check=True,
            capture_output=True
        )
        print(f"  ✅ Extracted: {csv_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Extraction failed: {e}")
        return False

def clean_text(text):
    """Clean and normalize text field"""
    if not text or text == "NA":
        return None
    return text.strip()

def parse_voter_count(value):
    """Parse voter count, return 0 if invalid"""
    if not value or value == "NA":
        return 0
    try:
        return int(value)
    except:
        return 0

def parse_coordinates(lat, lon):
    """Parse GPS coordinates, return None if invalid"""
    try:
        lat_float = float(lat) if lat and lat != "NA" else None
        lon_float = float(lon) if lon and lon != "NA" else None

        # Validate ranges
        if lat_float and (lat_float < -90 or lat_float > 90):
            return None, None
        if lon_float and (lon_float < -180 or lon_float > 180):
            return None, None

        return lat_float, lon_float
    except:
        return None, None

def generate_booth_code(state, district, ac_num, booth_num):
    """Generate unique booth code"""
    state_code = "TN" if state == "Tamil Nadu" else "PY"
    ac_code = f"AC{int(ac_num):03d}" if ac_num else "AC000"
    booth_code = f"B{int(booth_num):03d}" if booth_num else "B000"
    return f"{state_code}-{ac_code}-{booth_code}"

def convert_data():
    """Convert GitHub CSV to our format"""
    print(f"\n🔄 Step 3: Converting data to Pulse of People format...")

    csv_path = REPO_DIR / EXTRACTED_CSV
    if not csv_path.exists():
        print(f"  ❌ CSV file not found: {csv_path}")
        return False

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Output files
    wards_output = OUTPUT_DIR / "wards_from_github.csv"
    booths_output = OUTPUT_DIR / "polling_booths_from_github.csv"

    # Track unique wards and booths
    wards_set = set()
    booths_dict = {}

    print(f"  📖 Reading: {csv_path}")
    print(f"  🎯 Filtering for: {', '.join(TARGET_STATES)}")

    # Read and process
    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            stats["total_records"] += 1

            state = clean_text(row.get('state', ''))

            # Filter for target states
            if state not in TARGET_STATES:
                continue

            # Count by state
            if state == "Tamil Nadu":
                stats["tn_records"] += 1
            elif state == "Puducherry":
                stats["puducherry_records"] += 1

            # Extract fields
            district = clean_text(row.get('district', ''))
            ac_name = clean_text(row.get('ac_name', ''))
            ac_no = row.get('ac_no', '')
            ps_name = clean_text(row.get('ps_name', ''))
            ps_no = row.get('ps_no', '')
            address = clean_text(row.get('address', ''))
            building_type = clean_text(row.get('building_type', 'Other'))

            # Voter counts
            voters_male = parse_voter_count(row.get('male', 0))
            voters_female = parse_voter_count(row.get('female', 0))
            voters_third = parse_voter_count(row.get('third_gender', 0))
            voters_total = parse_voter_count(row.get('total', 0))

            # If total is 0, calculate from components
            if voters_total == 0:
                voters_total = voters_male + voters_female + voters_third

            # GPS coordinates
            lat, lon = parse_coordinates(
                row.get('latitude', ''),
                row.get('longitude', '')
            )

            # Infrastructure flags (1 = yes, 0 = no)
            electricity = row.get('electricity', '0') == '1'
            water = row.get('water', '0') == '1'
            toilet = row.get('toilet', '0') == '1'
            disabled_access = row.get('disabled', '0') == '1'

            # Generate unique booth code
            booth_code = generate_booth_code(state, district, ac_no, ps_no)

            # Skip if invalid data
            if not ps_name or not ac_name or voters_total == 0:
                stats["skipped_invalid"] += 1
                continue

            # Create ward entry (unique by AC)
            ward_key = f"{state}_{ac_no}"
            if ward_key not in wards_set:
                wards_set.add(ward_key)
                stats["wards_created"] += 1

            # Create booth entry (deduplicate by booth_code)
            if booth_code in booths_dict:
                stats["duplicates_removed"] += 1
                continue

            booths_dict[booth_code] = {
                'code': booth_code,
                'name': ps_name,
                'booth_number': ps_no,
                'address': address or f"{ps_name}, {district}, {state}",
                'latitude': lat or '',
                'longitude': lon or '',
                'total_voters': voters_total,
                'male_voters': voters_male,
                'female_voters': voters_female,
                'transgender_voters': voters_third,
                'building_type': building_type,
                'is_accessible': str(disabled_access).lower(),
                'has_electricity': str(electricity).lower(),
                'has_water': str(water).lower(),
                'has_toilet': str(toilet).lower(),
                'state': state,
                'district': district,
                'ac_name': ac_name,
                'ac_no': ac_no,
                'data_source': 'GitHub: in-rolls/poll-station-metadata',
                'data_date': '2018-2019',
            }
            stats["booths_created"] += 1

            # Progress indicator
            if stats["booths_created"] % 1000 == 0:
                print(f"  📊 Processed: {stats['booths_created']:,} booths...", end='\r')

    print()  # New line after progress

    # Write polling booths CSV
    print(f"\n  💾 Writing polling booths CSV...")
    with open(booths_output, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = [
            'code', 'booth_number', 'name', 'address',
            'latitude', 'longitude',
            'total_voters', 'male_voters', 'female_voters', 'transgender_voters',
            'building_type', 'is_accessible',
            'has_electricity', 'has_water', 'has_toilet',
            'state', 'district', 'ac_name', 'ac_no',
            'data_source', 'data_date'
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for booth in booths_dict.values():
            writer.writerow(booth)

    print(f"  ✅ Created: {booths_output}")
    print(f"  📊 Total booths: {len(booths_dict):,}")

    return True

def generate_summary_report():
    """Generate summary report"""
    print("\n" + "=" * 80)
    print(" 📊 CONVERSION SUMMARY")
    print("=" * 80)

    print(f"\n📥 Input Data:")
    print(f"  Total records processed: {stats['total_records']:,}")
    print(f"  Tamil Nadu records: {stats['tn_records']:,}")
    print(f"  Puducherry records: {stats['puducherry_records']:,}")

    print(f"\n📤 Output Data:")
    print(f"  Wards identified: {stats['wards_created']:,}")
    print(f"  Polling booths created: {stats['booths_created']:,}")
    print(f"  Duplicates removed: {stats['duplicates_removed']:,}")
    print(f"  Invalid records skipped: {stats['skipped_invalid']:,}")

    print(f"\n📁 Output Files:")
    booths_file = OUTPUT_DIR / "polling_booths_from_github.csv"
    if booths_file.exists():
        size_mb = booths_file.stat().st_size / (1024 * 1024)
        print(f"  {booths_file.name}")
        print(f"    Size: {size_mb:.2f} MB")
        print(f"    Rows: {stats['booths_created']:,}")
        print(f"    Location: {booths_file.absolute()}")

    print(f"\n✅ Next Steps:")
    print(f"  1. Review the CSV file: {booths_file}")
    print(f"  2. Login to your Pulse of People system")
    print(f"  3. Navigate to: Maps → Upload Booths")
    print(f"  4. Upload the CSV file")
    print(f"  5. Verify imported data in Booths List")

    print("\n" + "=" * 80)

    # Write summary to file
    summary_file = OUTPUT_DIR / "conversion_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("GitHub Electoral Data Conversion Summary\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Conversion Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source: in-rolls/poll-station-metadata (GitHub)\n\n")
        f.write(f"Total Records Processed: {stats['total_records']:,}\n")
        f.write(f"Tamil Nadu Records: {stats['tn_records']:,}\n")
        f.write(f"Puducherry Records: {stats['puducherry_records']:,}\n")
        f.write(f"Polling Booths Created: {stats['booths_created']:,}\n")
        f.write(f"Duplicates Removed: {stats['duplicates_removed']:,}\n")
        f.write(f"Invalid Records Skipped: {stats['skipped_invalid']:,}\n")

    print(f"📄 Summary saved to: {summary_file}")

def main():
    """Main execution"""
    print_banner()

    # Step 0: Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install required tools.")
        return 1

    # Step 1: Clone repository
    if not clone_repository():
        print("\n❌ Failed to clone repository")
        return 1

    # Step 2: Extract archive
    if not extract_archive():
        print("\n❌ Failed to extract archive")
        return 1

    # Step 3: Convert data
    if not convert_data():
        print("\n❌ Failed to convert data")
        return 1

    # Step 4: Generate summary
    generate_summary_report()

    print("\n✅ Conversion complete! Ready to upload to your system.")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Conversion cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
