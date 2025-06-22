#!/usr/bin/env python3
"""Web Scraping Example for DIGY.

This script demonstrates how to perform web scraping using requests and
BeautifulSoup. It fetches data from a website and extracts useful information.

Usage with DIGY:
    digy local . examples/web_scraping/website_scraper.py --url https://example.com
"""

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup



def is_valid_url(url: str) -> bool:
    """Check if a URL is valid.

    Args:
        url: The URL to validate

    Returns:
        bool: True if URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except (ValueError, AttributeError):
        return False



def get_page_links(url: str, max_links: int = 20) -> Dict[str, Any]:
    """Fetch a webpage and extract all links.

    Args:
        url: URL of the webpage to scrape
        max_links: Maximum number of links to return

    Returns:
        Dictionary containing page information and links
    """
    if not is_valid_url(url):
        return {"status": "error", "error": "Invalid URL"}

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
            'AppleWebKit/537.36'
        ),
        'Accept': (
            'text/html,application/xhtml+xml,application/xml;q=0.9,'
            'image/webp,*/*;q=0.8'
        ),
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        print(f"🌐 Fetching {url}")
        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True,
            verify=True
        )
        response.raise_for_status()

        # Check content type to ensure it's HTML
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            return {
                'url': url,
                'status': 'error',
                'error': f'Expected HTML, got {content_type}'
            }

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract page metadata
        title = soup.title.string if soup.title else "No title found"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else "No description"

        # Extract all unique links
        seen_links = set()
        links = []
        base_domain = urlparse(url).netloc

        for link in soup.find_all('a', href=True):
            if len(links) >= max_links:
                break

            href = link['href'].strip()
            if not href or href.startswith(('javascript:', 'mailto:', 'tel:')):
                continue

            # Convert relative URLs to absolute
            full_url = urljoin(url, href)
            full_url = full_url.split('#')[0]  # Remove fragment

            if is_valid_url(full_url) and full_url not in seen_links:
                seen_links.add(full_url)
                link_text = link.get_text(strip=True)[:150]  # Truncate text
                links.append({
                    'url': full_url,
                    'text': link_text,
                    'external': urlparse(full_url).netloc != base_domain
                })

        return {
            'url': url,
            'title': title,
            'description': description,
            'status': 'success',
            'links_found': len(links),
            'links': links
        }

    except requests.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_msg = f"HTTP {e.response.status_code}: {error_msg}"
        return {
            'url': url,
            'status': 'error',
            'error': error_msg
        }



def save_results(data: Dict[str, Any], output_dir: str = 'output') -> str:
    """Save scraping results to a JSON file.

    Args:
        data: Dictionary containing scrape results
        output_dir: Directory to save the output file

    Returns:
        str: Path to the saved file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create a safe filename from URL
    domain = urlparse(data.get('url', 'unknown')).netloc.replace('.', '_')
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"scrape_{domain}_{timestamp}.json"
    filepath = output_path / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 Results saved to {filepath}")
    return str(filepath)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    import argparse

    parser = argparse.ArgumentParser(description='Web Scraper')
    parser.add_argument(
        '--url',
        required=True,
        help='URL to scrape (e.g., https://example.com)'
    )
    parser.add_argument(
        '--output-dir',
        default='scrape_results',
        help='Directory to save output files (default: scrape_results)'
    )
    parser.add_argument(
        '--max-links',
        type=int,
        default=20,
        help='Maximum number of links to extract (default: 20)'
    )

    # Handle DIGY-style arguments (after --)
    if '--' in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    else:
        args = parser.parse_args()

    return args


def print_summary(results: Dict[str, Any]) -> None:
    """Print a summary of the scraping results.
    
    Args:
        results: Dictionary containing scraping results
    """
    if results.get('status') == 'error':
        print(f"❌ Error: {results.get('error', 'Unknown error')}")
        return

    print("\n📊 Scraping Results:")
    print(f"🌐 URL: {results.get('url')}")
    print(f"📝 Title: {results.get('title')}")
    print(f"🔗 Links found: {results.get('links_found', 0)}")
    print(f"📄 Description: {results.get('description', 'N/A')}")

    if 'links' in results and results['links']:
        print("\n🔗 Top links:")
        for i, link in enumerate(results['links'][:5], 1):
            print(f"  {i}. {link['url']}")
            if link.get('text'):
                print(f"     {link.get('text')}")

def main() -> None:
    """Run the web scraper with command line arguments."""
    args = parse_arguments()
    
    print(f"🔍 Starting web scraping of {args.url}")
    print(f"📂 Output directory: {args.output_dir}")
    print(f"🔗 Maximum links to extract: {args.max_links}")
    
    try:
        # Scrape the webpage
        results = get_page_links(args.url, max_links=args.max_links)
        
        # Save and display results
        if results.get('status') != 'error':
            output_file = save_results(results, args.output_dir)
            print(f"✅ Scraping complete! Results saved to {output_file}")
        
        print_summary(results)
        
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
