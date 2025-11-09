#!/usr/bin/env python3
"""
Tamil Nadu & Puducherry Electoral Data Downloader
Downloads polling station PDFs from official CEO websites
"""

import os
import requests
from pathlib import Path
from urllib.parse import urljoin

# Configuration
BASE_URL_TN = "https://www.elections.tn.gov.in/PSLIST_20012021"
OUTPUT_DIR = Path("downloaded_pdfs")

# Tamil Nadu Districts (1-37) and their constituencies
TN_DISTRICTS = {
    1: {"name": "Tiruvallur", "constituencies": list(range(1, 7))},  # AC001-AC006
    2: {"name": "Chennai", "constituencies": list(range(7, 24))},     # AC007-AC023
    3: {"name": "Kanchipuram", "constituencies": list(range(24, 34))}, # AC024-AC033
    # ... Add remaining 34 districts
    # Full mapping available at: https://www.elections.tn.gov.in
}

def download_pdf(url, output_path):
    """Download a PDF file from URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"✅ Downloaded: {output_path.name}")
        return True
    except Exception as e:
        print(f"❌ Failed: {output_path.name} - {e}")
        return False

def download_tn_constituency(district_num, ac_num, language="English"):
    """Download polling station list for a Tamil Nadu constituency"""
    # URL pattern: PSLIST_20012021/dt{district}/{language}/AC{number}.pdf
    ac_code = f"AC{ac_num:03d}"
    pdf_url = f"{BASE_URL_TN}/dt{district_num}/{language}/{ac_code}.pdf"

    # Create output directory
    output_dir = OUTPUT_DIR / f"TN_dt{district_num}" / language
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{ac_code}.pdf"

    if output_path.exists():
        print(f"⏭️  Skipped (already exists): {ac_code}")
        return True

    return download_pdf(pdf_url, output_path)

def download_sample_data():
    """Download sample data from first 5 constituencies"""
    print("=" * 60)
    print("Tamil Nadu Electoral Data Downloader")
    print("=" * 60)
    print("\n📥 Downloading sample data from first 5 constituencies...\n")

    # Download first 5 constituencies from Tiruvallur district
    success_count = 0
    for ac_num in range(1, 6):  # AC001 to AC005
        if download_tn_constituency(1, ac_num, "English"):
            success_count += 1

    print(f"\n✅ Successfully downloaded: {success_count}/5 PDFs")
    print(f"📁 Saved to: {OUTPUT_DIR.absolute()}")
    print("\n💡 Next Steps:")
    print("1. Install Tabula: Download from https://tabula.technology/")
    print("2. Open downloaded PDFs in Tabula")
    print("3. Extract booth tables to CSV")
    print("4. Upload CSV via your Wards/Booths upload page")

def download_all_tn_data():
    """Download all 234 Tamil Nadu constituencies"""
    print("=" * 60)
    print("FULL DOWNLOAD: All 234 Tamil Nadu Constituencies")
    print("=" * 60)
    print("\n⚠️  This will download ~234 PDF files (~500MB total)")

    confirm = input("\nProceed? (yes/no): ")
    if confirm.lower() != "yes":
        print("Download cancelled.")
        return

    total = 0
    success = 0

    for district_num, district_data in TN_DISTRICTS.items():
        print(f"\n📂 District {district_num}: {district_data['name']}")

        for ac_num in district_data['constituencies']:
            if download_tn_constituency(district_num, ac_num, "English"):
                success += 1
            total += 1

    print(f"\n{'=' * 60}")
    print(f"✅ Download Complete: {success}/{total} PDFs")
    print(f"📁 Location: {OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Tamil Nadu & Puducherry Electoral Data Downloader")
    print("=" * 60)
    print("\nOptions:")
    print("1. Download sample data (5 constituencies)")
    print("2. Download all Tamil Nadu data (234 constituencies)")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ")

    if choice == "1":
        download_sample_data()
    elif choice == "2":
        download_all_tn_data()
    else:
        print("Goodbye!")
