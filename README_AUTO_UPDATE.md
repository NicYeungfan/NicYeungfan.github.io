# Auto-Update Agent for Google Scholar Publications

This repository includes an automated system to sync publications from Google Scholar to the personal website.

## Overview

The auto-update agent:
1. Fetches publications from your Google Scholar profile
2. Detects new or updated publications
3. Automatically updates the `index.html` file
4. Commits and pushes changes to GitHub

## Files

- `update_publications.py` - Main script that fetches and updates publications
- `requirements.txt` - Python dependencies
- `.github/workflows/update-publications.yml` - GitHub Actions workflow for automation

## Setup

### Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the script manually:
```bash
python update_publications.py
```

### Automatic Updates via GitHub Actions

The workflow is configured to run automatically:
- **Schedule**: Daily at 2 AM UTC (10 AM HKT)
- **Manual trigger**: Available in GitHub Actions tab

The workflow will:
1. Checkout the repository
2. Install dependencies
3. Run the update script
4. Commit and push changes if any publications were updated

## How It Works

### Method 1: Scholarly Library (Preferred)
The script first tries to use the `scholarly` library, which provides a more reliable way to access Google Scholar data.

### Method 2: Web Scraping (Fallback)
If the scholarly library is not available or fails, the script falls back to web scraping using BeautifulSoup and requests.

## Configuration

Edit the following variables in `update_publications.py`:
- `SCHOLAR_USER_ID`: Your Google Scholar user ID (default: `FDrOozwAAAAJ`)
- `SCHOLAR_URL`: Your Google Scholar profile URL
- `max_publications`: Number of publications to display (default: 10)

## Impact Factor Mapping

The script includes a mapping of journal names to impact factors. To add more journals, edit the `get_journal_impact_factor()` function in `update_publications.py`.

## Troubleshooting

### Google Scholar Blocking
If Google Scholar blocks the requests:
1. The script will try to install the `scholarly` library automatically
2. You may need to add delays between requests
3. Consider using a proxy or VPN

### No Publications Found
- Check that your Google Scholar profile is public
- Verify the user ID is correct
- Check network connectivity

### HTML Update Fails
- Ensure `index.html` exists in the repository root
- Check that the HTML structure matches expected format
- Review error messages in the script output

## Manual Updates

You can also trigger updates manually:
1. Go to the GitHub repository
2. Navigate to "Actions" tab
3. Select "Update Publications from Google Scholar"
4. Click "Run workflow"

## Notes

- The script preserves the existing HTML structure and styling
- Only the publications section is updated
- The script is designed to be idempotent (safe to run multiple times)
- Changes are only committed if publications are actually updated

