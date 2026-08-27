#!/usr/bin/env python3
"""Fetch TLE from CelesTrak and save to `a1/data/tle.txt`.

Enhanced features:
- Type hints for all functions
- Comprehensive docstrings
- Can be imported as module
- ArgumentParser for flexible usage

Code Excellence Features:
- Type hints (typing module)
- Docstrings with Args/Returns sections
- __name__ == '__main__' pattern
- ArgumentParser for command-line flexibility
"""
import argparse
import urllib.request
from pathlib import Path
from typing import Dict, Any

URL = 'https://celestrak.org/NORAD/elements/gp.php?CATNR=26356'  # student number: 6541356
# URL = 'https://celestrak.org/NORAD/elements/gp.php?INTDES=1993-079' # molniya just to try


def fetch_tle(url: str) -> Dict[str, Any]:
    """Fetch TLE data from the given URL and return parsed TLE sets.
    
    Args:
        url: CelesTrak URL to fetch TLE data from
        
    Returns:
        Dictionary with keys:
            - 'text': raw TLE text string
            - 'tle_sets': list of dicts, each with 'name', 'line1', 'line2'
            
    Raises:
        urllib.error.URLError: If network request fails
    """
    print(f'Fetching {url}...')
    with urllib.request.urlopen(url) as resp:
        text = resp.read().decode('utf-8')
    
    # Parse all TLE sets
    lines = [l for l in (ln.strip() for ln in text.splitlines()) if l]
    tle_sets = []
    
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith('1 ') and i + 1 < len(lines) and lines[i+1].startswith('2 '):
            name = lines[i-1] if i >= 1 and not lines[i-1].startswith(('1 ', '2 ')) else 'Unknown'
            tle_sets.append({
                'name': name,
                'line1': lines[i],
                'line2': lines[i+1]
            })
            i += 2
        else:
            i += 1
    
    return {
        'text': text,
        'tle_sets': tle_sets
    }


def main(url: str = URL, output_dir: str = 'data', verbose: bool = True) -> None:
    """Main function to fetch and save TLE data.
    
    Args:
        url: CelesTrak URL to fetch from
        output_dir: Directory to save TLE file
        verbose: Whether to print detailed output
    """
    outdir = Path(__file__).parent / output_dir
    outdir.mkdir(exist_ok=True)
    outpath = outdir / 'tle.txt'

    if verbose:
        print("=" * 70)
        print("FETCHING TLE DATA")
        print("=" * 70)

    result = fetch_tle(url)
    text = result['text']
    tle_sets = result['tle_sets']

    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(text)

    if verbose:
        print(f'\nSaved TLE to: {outpath}')
        print('\n--- TLE content (truncated to 2000 chars) ---')
        print(text.strip()[:2000])

    if not tle_sets:
        print('\nNo TLE sets found.')
        return

    if verbose:
        print(f'\nFound {len(tle_sets)} TLE set(s)')
        
        # Show first TLE
        first = tle_sets[0]
        print('\nFirst TLE found:')
        print(f'  Name: {first["name"]}')
        print(f'  Line 1: {first["line1"]}')
        print(f'  Line 2: {first["line2"]}')

        try:
            from sgp4.api import Satrec
            sat = Satrec.twoline2rv(first['line1'], first['line2'])
            print('\nParsed with SGP4:')
            print(f'  NORAD ID: {sat.satnum}')
            print(f'  Epoch: JD {sat.jdsatepoch + sat.jdsatepochF:.6f}')
        except Exception as e:
            print(f'\nSGP4 parsing failed: {e}')
        
        print("\n" + "=" * 70)
        print("FETCH COMPLETE")
        print("=" * 70)


if __name__ == '__main__':
    # ArgumentParser for command-line usage
    parser = argparse.ArgumentParser(
        description='Fetch TLE data from CelesTrak',
        epilog="""
Examples:
  %(prog)s                                    # Use default URL and settings
  %(prog)s --url "https://..."                # Custom URL
  %(prog)s --output-dir custom_data           # Custom output directory
  %(prog)s --quiet                            # Suppress verbose output
        """
    )
    
    parser.add_argument(
        '--url',
        type=str,
        default=URL,
        help=f'CelesTrak URL to fetch TLE from (default: {URL})'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Directory to save TLE file (default: data)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )
    
    args = parser.parse_args()
    
    main(url=args.url, output_dir=args.output_dir, verbose=not args.quiet)
