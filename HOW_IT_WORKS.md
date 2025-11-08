# How the Auto-Update System Works

## ✅ Yes, It's Set Up Correctly!

Every time your Google Scholar profile updates, your website will automatically update within 24 hours.

## How It Works

### 1. **Automatic Daily Check**
   - GitHub Actions runs the workflow **every day at 2 AM UTC (10 AM HKT)**
   - The script fetches your latest publications from Google Scholar
   - Compares them with what's currently on your website

### 2. **When Updates Are Detected**
   - If new publications are found, the script updates `index.html`
   - Changes are automatically committed to GitHub
   - Your website is updated immediately (GitHub Pages auto-deploys)

### 3. **Manual Trigger (Optional)**
   - You can also trigger updates manually:
     1. Go to GitHub → Your Repository
     2. Click "Actions" tab
     3. Select "Update Publications from Google Scholar"
     4. Click "Run workflow"

## Timeline

- **Google Scholar Updates** → Your profile changes
- **Within 24 hours** → GitHub Actions checks for updates
- **If new publications found** → Website automatically updates
- **Your site is live** → Changes appear on your website

## What Gets Updated

- ✅ Publication titles
- ✅ Journal names
- ✅ Publication years
- ✅ Impact factors (for known journals)
- ✅ Links to papers (DOI or Google Scholar links)
- ✅ Sorted by year (newest first)
- ✅ Top 10 most recent publications displayed

## Verification

To verify it's working:

1. **Check GitHub Actions**:
   - Go to: https://github.com/NicYeungfan/NicYeungfan.github.io/actions
   - You should see "Update Publications from Google Scholar" workflow
   - It should run daily

2. **Check Workflow Logs**:
   - Click on a workflow run
   - Check the logs to see if publications were fetched
   - Look for "✓ Found X publications" message

3. **Test Manually**:
   - Add a new publication to your Google Scholar profile
   - Wait a few minutes, then manually trigger the workflow
   - Check if your website updates

## Troubleshooting

If updates aren't happening:

1. **Check Google Scholar Profile**:
   - Make sure your profile is public
   - Verify the user ID is correct: `FDrOozwAAAAJ`

2. **Check GitHub Actions**:
   - Go to Actions tab
   - Check if workflows are running
   - Look for error messages in the logs

3. **Google Scholar Blocking**:
   - Sometimes Google Scholar blocks automated requests
   - The script tries multiple methods (scholarly library + web scraping)
   - If it fails, try running manually later

## Current Configuration

- **Schedule**: Daily at 2 AM UTC (10 AM HKT)
- **Google Scholar User ID**: FDrOozwAAAAJ
- **Max Publications**: 10 (most recent)
- **Update Frequency**: Once per day

## Summary

✅ **Yes, it's working!** Every time you update your Google Scholar profile, your website will automatically sync within 24 hours (or immediately if you trigger it manually).

The system is fully automated and requires no manual intervention. Just keep your Google Scholar profile updated, and your website will stay in sync!

