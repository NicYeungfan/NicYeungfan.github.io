#!/usr/bin/env python3
"""
Advanced auto-update agent for Google Scholar publications
Uses multiple methods to fetch publications and update the website
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import html
import os
import sys
import time
import subprocess

# Google Scholar profile URL
SCHOLAR_URL = "https://scholar.google.com/citations?user=FDrOozwAAAAJ&hl=zh-TW"
SCHOLAR_USER_ID = "FDrOozwAAAAJ"

# Headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}

def fetch_with_scholarly():
    """
    Try to fetch publications using scholarly library
    This is more reliable but requires the library
    """
    try:
        from scholarly import scholarly
        
        author = scholarly.search_author_id(SCHOLAR_USER_ID)
        author = scholarly.fill(author)
        
        publications = []
        for pub in author.get('publications', [])[:20]:  # Limit to 20 most recent
            try:
                pub_filled = scholarly.fill(pub)
                title = pub_filled.get('bib', {}).get('title', '')
                authors = ', '.join(pub_filled.get('bib', {}).get('author', []))
                venue = pub_filled.get('bib', {}).get('venue', '')
                year = pub_filled.get('bib', {}).get('pub_year', '')
                pub_url = pub_filled.get('pub_url', '')
                citations = pub_filled.get('num_citations', 0)
                
                if title:
                    publications.append({
                        'title': title,
                        'authors': authors,
                        'venue': venue,
                        'year': str(year) if year else '',
                        'citations': str(citations),
                        'url': pub_url
                    })
            except Exception as e:
                print(f"Error processing publication with scholarly: {e}")
                continue
        
        return publications
    except ImportError:
        print("scholarly library not available, falling back to web scraping")
        return None
    except Exception as e:
        print(f"Error using scholarly library: {e}")
        return None

def fetch_scholar_publications():
    """
    Fetch publications from Google Scholar profile
    Returns a list of publication dictionaries
    """
    # First, try scholarly library
    publications = fetch_with_scholarly()
    if publications:
        return publications
    
    # Fallback to web scraping
    publications = []
    
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        
        # Add delay to avoid rate limiting
        time.sleep(2)
        
        response = session.get(SCHOLAR_URL, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all publication entries - Google Scholar uses different class names
        pub_rows = soup.find_all('tr', class_='gsc_a_tr') or soup.find_all('tr', {'class': re.compile(r'gsc_a_tr')})
        
        if not pub_rows:
            # Try alternative selectors
            pub_rows = soup.find_all('tr', id=re.compile(r'gsc_a_tr'))
        
        for row in pub_rows:
            try:
                # Extract title
                title_elem = row.find('a', class_='gsc_a_at') or row.find('a', {'class': re.compile(r'gsc_a_at')})
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                href = title_elem.get('href', '')
                pub_url = "https://scholar.google.com" + href if href.startswith('/') else href
                
                # Extract authors and venue
                gray_divs = row.find_all('div', class_='gs_gray') or row.find_all('div', {'class': re.compile(r'gs_gray')})
                authors = ""
                venue = ""
                
                if len(gray_divs) > 0:
                    authors = gray_divs[0].get_text(strip=True)
                if len(gray_divs) > 1:
                    venue_text = gray_divs[1].get_text(strip=True)
                    # Extract year from venue text
                    year_match = re.search(r'(\d{4})', venue_text)
                    if year_match:
                        year = year_match.group(1)
                        venue = venue_text.replace(year, '').strip().rstrip(',').strip()
                    else:
                        venue = venue_text
                
                # Extract year separately if available
                year_elem = row.find('span', class_='gsc_a_y') or row.find('span', {'class': re.compile(r'gsc_a_y')})
                year = year_elem.get_text(strip=True) if year_elem else ""
                
                # Extract citations
                citations_elem = row.find('a', class_='gsc_a_c') or row.find('a', {'class': re.compile(r'gsc_a_c')})
                citations = citations_elem.get_text(strip=True) if citations_elem else "0"
                
                publications.append({
                    'title': title,
                    'authors': authors,
                    'venue': venue,
                    'year': year,
                    'citations': citations,
                    'url': pub_url
                })
                
            except Exception as e:
                print(f"Error parsing publication: {e}")
                continue
                
    except requests.RequestException as e:
        print(f"Error fetching Google Scholar page: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    
    return publications

def extract_doi_from_text(text):
    """Extract DOI from text"""
    doi_pattern = r'10\.\d{4,}/[^\s\)]+'
    match = re.search(doi_pattern, text)
    if match:
        doi = match.group(0).rstrip('.,;')
        return f"https://doi.org/{doi}"
    return None

def get_journal_impact_factor(journal_name):
    """Map journal names to impact factors"""
    impact_factors = {
        'Applied Energy': 11.2,
        'Journal of Energy Storage': 9.8,
        'Remote Sensing': 5.0,
        'Sensors': 3.9,
        'Sustainable Energy Technologies and Assessments': 7.0,
        'IEEE Transactions': 3.0,  # Default for IEEE
    }
    
    journal_lower = journal_name.lower()
    for journal, if_val in impact_factors.items():
        if journal.lower() in journal_lower:
            return if_val
    return None

def parse_current_publications(html_content):
    """Parse existing publications from the HTML file"""
    soup = BeautifulSoup(html_content, 'html.parser')
    publications = []
    
    pub_items = soup.find_all('div', class_='publication-item')
    for item in pub_items:
        title_elem = item.find('div', class_='publication-title')
        if title_elem:
            publications.append(title_elem.get_text(strip=True).lower())
    
    return publications

def create_publication_html(publication):
    """Create HTML for a publication item"""
    title = publication.get('title', '').strip()
    if not title:
        return ""
    
    # Try to extract DOI from various sources
    doi_link = None
    if publication.get('url'):
        doi_link = extract_doi_from_text(publication['url'])
    
    if not doi_link and title:
        doi_link = extract_doi_from_text(title)
    
    # Get journal and impact factor
    journal_name = publication.get('venue', '').strip()
    impact_factor = get_journal_impact_factor(journal_name)
    if_val_str = f" (IF = {impact_factor})" if impact_factor else ""
    
    # Format year
    year = publication.get('year', '').strip()
    if not year:
        year = str(datetime.now().year)
    
    # Clean journal name
    if journal_name:
        journal_display = f"{journal_name}, {year}"
    else:
        journal_display = year
    
    html_content = f"""                <div class="publication-item">
                    <div class="publication-title">{html.escape(title)}</div>
                    <div class="publication-journal">{html.escape(journal_display)}{if_val_str}</div>
                    <div class="publication-links">"""
    
    if doi_link:
        html_content += f'\n                        <a href="{doi_link}">Read Paper</a>'
    elif publication.get('url') and 'scholar.google.com' in publication['url']:
        html_content += f'\n                        <a href="{publication["url"]}">View on Google Scholar</a>'
    
    html_content += """
                    </div>
                </div>"""
    
    return html_content

def update_html_file(html_file_path, new_publications, max_publications=10):
    """Update the HTML file with new publications"""
    try:
        # Read current HTML
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the publications section
        publications_section = soup.find('section', id='publications')
        if not publications_section:
            print("Error: Publications section not found in HTML")
            return False
        
        # Get existing publication titles
        existing_titles = parse_current_publications(html_content)
        
        # Remove all existing publication items
        for pub_item in publications_section.find_all('div', class_='publication-item'):
            pub_item.decompose()
        
        # Filter and sort publications
        # Sort by year (most recent first), then by title for stability
        def sort_key(pub):
            year = pub.get('year', '0')
            try:
                year_int = int(year) if year.isdigit() else 0
            except:
                year_int = 0
            return (-year_int, pub.get('title', '').lower())
        
        sorted_pubs = sorted(new_publications, key=sort_key)
        
        # Limit to max_publications
        recent_pubs = sorted_pubs[:max_publications]
        
        # Find where to insert (before the "View Complete Publication List" paragraph)
        view_all_paragraph = None
        for p in publications_section.find_all('p'):
            if 'View Complete Publication List' in p.get_text() or 'Google Scholar' in p.get_text():
                view_all_paragraph = p
                break
        
        # Insert new publications
        for pub in recent_pubs:
            pub_html = create_publication_html(pub)
            if pub_html:
                pub_soup = BeautifulSoup(pub_html, 'html.parser')
                if view_all_paragraph:
                    view_all_paragraph.insert_before(pub_soup)
                else:
                    # Append to section if no view all link found
                    publications_section.append(pub_soup)
        
        # Write updated HTML (preserve formatting)
        updated_html = str(soup)
        
        # Preserve the original structure better
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_html)
        
        return True
        
    except Exception as e:
        print(f"Error updating HTML file: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to update publications"""
    print("=" * 60)
    print("Google Scholar Publication Auto-Updater")
    print("=" * 60)
    print(f"Fetching publications for user: {SCHOLAR_USER_ID}")
    print(f"URL: {SCHOLAR_URL}")
    print()
    
    # Fetch publications from Google Scholar
    publications = fetch_scholar_publications()
    
    if not publications:
        print("ERROR: No publications found or error occurred")
        print("This could be due to:")
        print("1. Google Scholar blocking the request")
        print("2. Network issues")
        print("3. Changes in Google Scholar's HTML structure")
        print("\nTrying to install scholarly library for better results...")
        
        # Try to install scholarly
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'scholarly', '--quiet'])
            print("Installed scholarly library, retrying...")
            publications = fetch_scholar_publications()
        except:
            print("Could not install scholarly library automatically")
        
        if not publications:
            return 1
    
    print(f"✓ Found {len(publications)} publications")
    
    # Display first few publications
    print("\nSample publications:")
    for i, pub in enumerate(publications[:3], 1):
        print(f"  {i}. {pub.get('title', 'N/A')[:60]}... ({pub.get('year', 'N/A')})")
    
    # Update HTML file
    html_file = 'index.html'
    if not os.path.exists(html_file):
        print(f"ERROR: {html_file} not found in current directory")
        return 1
    
    print(f"\nUpdating {html_file}...")
    success = update_html_file(html_file, publications, max_publications=10)
    
    if success:
        print(f"✓ Successfully updated {html_file}")
        print(f"  Added/updated {min(10, len(publications))} publications")
        return 0
    else:
        print("ERROR: Failed to update HTML file")
        return 1

if __name__ == '__main__':
    sys.exit(main())
