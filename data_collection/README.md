# Polling Booth Data Collection - Tamil Nadu & Puducherry

**Project**: Pulse of People Platform
**Mission**: Collect ward and polling booth data for 264 constituencies (25,000-30,000 booths)
**Status**: ✅ Research Complete - Ready for Data Collection
**Date**: 2025-11-09

---

## Quick Navigation

### For Quick Start
👉 **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Start here if you're Agent 2 (Data Collection)

### For Complete Information
📖 **[DATA_COLLECTION_REPORT.md](DATA_COLLECTION_REPORT.md)** - Full research report (824 lines, 15 sections)

### For Executive Summary
📊 **[RESEARCH_SUMMARY.md](RESEARCH_SUMMARY.md)** - Key findings and recommendations

### For Quick Reference
📋 **[DATA_SOURCES_SUMMARY.csv](DATA_SOURCES_SUMMARY.csv)** - 25 data sources at a glance

### For Data Structure
🗂️ **[polling_booths_template.csv](polling_booths_template.csv)** - CSV schema with example row

---

## Project Overview

### Scope
- **Tamil Nadu**: 234 assembly constituencies
- **Puducherry**: 30 constituencies
- **Total Target**: 25,000-30,000 polling booths
- **Data Points**: Booth names, addresses, voter counts, GPS coordinates, infrastructure

### Success Criteria
- ✅ 95%+ constituency coverage (250+ of 264)
- ✅ 25,000+ polling booths collected
- ✅ 95%+ data completeness (all key fields)
- ✅ 98%+ data accuracy (validated against official sources)

---

## File Manifest

### Documentation (1,594 lines total)

| File | Size | Lines | Purpose |
|------|------|-------|---------|
| **DATA_COLLECTION_REPORT.md** | 29 KB | 824 | Comprehensive research findings, all data sources, acquisition strategy, data schema, validation framework |
| **RESEARCH_SUMMARY.md** | 15 KB | 404 | Executive summary, key findings, recommendations, next steps |
| **QUICK_START_GUIDE.md** | 8.1 KB | 247 | Step-by-step instructions for data collection, code snippets, troubleshooting |
| **DATA_SOURCES_SUMMARY.csv** | 4.5 KB | 26 | Quick reference table of 25 data sources with URLs and priorities |
| **polling_booths_template.csv** | 640 B | 2 | CSV schema definition with sample row (23 columns) |
| **README.md** | - | - | This file (navigation guide) |

### Directory Structure

```
data_collection/
├── README.md                          # This file
├── DATA_COLLECTION_REPORT.md          # Full research report
├── RESEARCH_SUMMARY.md                # Executive summary
├── QUICK_START_GUIDE.md               # How to start data collection
├── DATA_SOURCES_SUMMARY.csv           # 25 data sources reference
├── polling_booths_template.csv        # CSV schema template
├── raw/                               # Raw downloaded data
│   ├── tamil_nadu/                    # TN PDFs, CSVs by district
│   └── puducherry/                    # Puducherry data files
└── processed/                         # Cleaned, validated outputs
    ├── polling_booths_master.csv      # Final master dataset (to be created)
    ├── constituencies_master.csv      # 264 constituencies (to be created)
    └── wards_master.csv               # Ward mappings (to be created)
```

---

## Research Phase Results

### Data Sources Identified: 25+

**Official Government** (10 sources):
- Election Commission of India Portal
- Tamil Nadu CEO Office (3 portals)
- Puducherry CEO Office (2 portals)
- 4+ District-level government portals

**GitHub Repositories** (4 sources):
- in-rolls/poll-station-metadata (989K booths, 32 states)
- in-rolls/electoral_rolls (Tamil Nadu 2018 data)
- in-rolls/parse_searchable_rolls (parsing tools)
- datameet/india-election-data (elections datasets)

**Third-Party Aggregators** (11 sources):
- Dataful.in, MyNeta.info, Elections.in, VotersList.in, etc.

### Data Availability: 95%+ Confidence
✅ All 264 constituencies have data available
✅ Multiple fallback sources identified
✅ Pre-parsed datasets found (GitHub)
✅ Current 2025 electoral rolls accessible
✅ Tools and scripts available

---

## Recommended Data Collection Strategy

### Phase 1: GitHub Quick Win (2-3 hours)
**Source**: in-rolls/poll-station-metadata
**Action**: Clone repository, extract 7z, filter for Tamil Nadu
**Output**: 20,000+ booths with infrastructure metadata

```bash
gh repo clone in-rolls/poll-station-metadata
7z x poll_station_metadata_all.7z
grep "Tamil Nadu" poll_station_metadata_all.csv > tn_booths.csv
```

### Phase 2: Official 2025 Data (10-15 hours, parallelizable)
**Source**: ECI Portal + TN CEO PDFs
**Priority Order**:
1. Chennai (16 AC, ~3,000 booths)
2. Coimbatore, Madurai, Tiruchirappalli, Salem (38 AC, ~6,000 booths)
3. Remaining 180 AC (~16,000 booths)
4. Puducherry (30 AC, ~2,000 booths)

**Download Options**:
- **Option A**: Manual ECI portal (https://voters.eci.gov.in/download-eroll)
- **Option B**: Automated TN CEO PDFs (https://www.elections.tn.gov.in/Web/pslist/ac###.pdf)
- **Option C**: Browser automation (Selenium for ECI portal)

### Phase 3: Validation & Enrichment (3-4 hours)
- Deduplicate booths across sources
- Geocode missing GPS coordinates (target: 80%+)
- Cross-validate voter totals
- Generate data quality report

---

## Data Schema (23 Columns)

### Location Fields (6)
state, district, assembly_constituency_number, assembly_constituency_name, ward_number, ward_name

### Polling Station Fields (4)
polling_station_number, polling_station_name, polling_station_address, part_number

### Geographic Fields (2)
latitude, longitude

### Voter Statistics (4)
voters_male, voters_female, voters_third_gender, voters_total

### Infrastructure (5)
building_type, accessible_for_disabled, electricity_available, water_available, toilet_available

### Metadata (3)
data_source, data_collection_date, notes

**See**: [polling_booths_template.csv](polling_booths_template.csv) for example

---

## Timeline Estimates

### Solo Effort (Agent 2)
- GitHub Data Collection: 0.5 days
- Official Portal Downloads: 2 days
- PDF Parsing: 2.5 days
- Puducherry Collection: 0.5 days
- Validation & Cleanup: 1 day
- **TOTAL**: **7-8 days**

### Team Effort (5 people)
- Data Collection (parallelized): 0.5 days
- Parsing (automated): 2.5 days
- Validation (distributed): 0.5 days
- **TOTAL**: **2-3 days**

---

## Key URLs (Quick Access)

### Start Data Collection
- **ECI Portal**: https://voters.eci.gov.in/download-eroll
- **TN CEO Polling Stations**: https://www.elections.tn.gov.in/pslist_inet.aspx
- **GitHub Metadata Repo**: https://github.com/in-rolls/poll-station-metadata

### Reference
- **TN Constituencies List**: https://en.wikipedia.org/wiki/List_of_constituencies_of_the_Tamil_Nadu_Legislative_Assembly
- **Harvard Dataverse (Parsed Data)**: http://dx.doi.org/10.7910/DVN/MUEGDT

### Support
- **TN CEO Contact**: ceo@tn.gov.in | 1800 4252 1950

---

## Next Steps

### For Agent 2 (Data Collection Specialist)

1. **Read Quick Start Guide** (30 min)
   - Review [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)
   - Choose Option A, B, or C

2. **Test Collection** (2 hours)
   - Download 2-3 sample constituencies
   - Test PDF parsing
   - Validate against template

3. **Execute Priority 1** (1-2 days)
   - Collect Chennai (16 AC)
   - Run Checkpoint 1 validation
   - Report progress

4. **Scale to Full Dataset** (5-6 days)
   - Continue with Priority 2 & 3 cities
   - Complete Puducherry
   - Final validation

5. **Deliver Final Dataset**
   - polling_booths_master.csv (25,000+ rows)
   - constituencies_master.csv (264 rows)
   - Data quality report

---

## Tools Needed

### Python Libraries
```bash
pip install pdfplumber tabula-py pandas selenium beautifulsoup4 geopy
```

### Command-Line Tools
```bash
# PDF downloads
wget, curl

# Repository cloning
git, gh

# Archive extraction
7z

# PDF text extraction (fallback)
pdftotext, tesseract (OCR)
```

---

## Success Metrics

| Metric | Target | Minimum |
|--------|--------|---------|
| Total Booths | 27,000 | 25,000 |
| Constituencies | 264 (100%) | 250 (95%) |
| Completeness | 95% | 85% |
| Accuracy | 98% | 95% |
| GPS Coverage | 80% | 60% |

---

## Contact & Support

**Questions?**
- Review full documentation in DATA_COLLECTION_REPORT.md
- Check troubleshooting in QUICK_START_GUIDE.md
- Contact Tamil Nadu CEO: ceo@tn.gov.in

**Issues?**
- Document in data_collection_logs/ (to be created)
- Track parsing errors for pattern analysis
- Report blockers immediately

---

## Version History

| Version | Date | Agent | Changes |
|---------|------|-------|---------|
| 1.0 | 2025-11-09 | Agent 1 | Initial research phase complete |
| - | - | Agent 2 | Data collection phase (pending) |
| - | - | Agent 3 | Validation & integration (pending) |

---

## Project Status

- ✅ **Phase 1: Research** - COMPLETE (Agent 1)
- 🔄 **Phase 2: Data Collection** - READY TO START (Agent 2)
- ⏳ **Phase 3: Validation** - PENDING (Agent 3)
- ⏳ **Phase 4: Integration** - PENDING (Backend Team)

---

**Last Updated**: 2025-11-09
**Prepared By**: Agent 1 - Research & Data Collection Specialist
**Status**: ✅ Research Complete - Ready for Data Collection

---

## Quick Commands

**View all documentation**:
```bash
cd /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/data_collection
ls -lh
```

**Start data collection (Option A - GitHub)**:
```bash
gh repo clone in-rolls/poll-station-metadata
cd poll-station-metadata
7z x poll_station_metadata_all.7z
```

**Download TN CEO PDFs (Option B)**:
```bash
cd /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/data_collection/raw/tamil_nadu
for i in {1..234}; do
  ac_num=$(printf "%03d" $i)
  wget "https://www.elections.tn.gov.in/Web/pslist/ac${ac_num}.pdf" -O "AC${ac_num}.pdf"
  sleep 2
done
```

**Parse sample PDF**:
```bash
python3 -m pip install pdfplumber
python3 -c "
import pdfplumber
with pdfplumber.open('AC001.pdf') as pdf:
    for page in pdf.pages:
        print(page.extract_table())
"
```

---

**Ready to begin data collection!** 🚀

See **QUICK_START_GUIDE.md** for detailed step-by-step instructions.
