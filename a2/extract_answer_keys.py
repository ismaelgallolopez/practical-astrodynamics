#!/usr/bin/env python3
"""
Extract answer keys from README.md and verify answer-sheet.yaml completeness.

Uses regex to parse the assignment README and identify all required answer keys.
"""

import re
import yaml
from pathlib import Path


def extract_answer_keys_from_readme(readme_path='README.md'):
    """
    Extract all answer keys from the assignment README file.
    
    Returns:
        Dictionary mapping answer keys to their point values
    """
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Pattern to match answer keys like: ss_REG_OrbKep_CODE_1.5
    # Format: [ls|ss|li|lf|sf]_[REG|MDT|AEX|CEX]_[Name]_[TYPE]_[points]
    pattern = r'\b([ls][sfi])_([A-Z]{3})_([A-Za-z0-9]+)_([A-Z]+)_([0-9.]+)\b'
    
    matches = re.findall(pattern, content)
    
    answer_keys = {}
    for match in matches:
        prefix, category, name, type_code, points = match
        key = f"{prefix}_{category}_{name}_{type_code}_{points}"
        answer_keys[key] = float(points)
    
    return answer_keys


def load_answer_sheet(yaml_path='answer-sheet.yaml'):
    """Load the answer sheet YAML file."""
    try:
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: {yaml_path} not found")
        return {}


def verify_completeness(required_keys, answer_sheet):
    """
    Verify that all required answer keys are present in the answer sheet.
    
    Returns:
        Tuple of (missing_keys, extra_keys, total_points_possible, points_covered)
    """
    required_set = set(required_keys.keys())
    provided_set = set(answer_sheet.keys()) if answer_sheet else set()
    
    missing = required_set - provided_set
    extra = provided_set - required_set
    
    total_points = sum(required_keys.values())
    covered_points = sum(required_keys[k] for k in required_set & provided_set)
    
    return missing, extra, total_points, covered_points


def print_results(required_keys, missing, extra, total_points, covered_points):
    """Print verification results."""
    print("=" * 80)
    print("ANSWER KEY EXTRACTION AND VERIFICATION")
    print("=" * 80)
    
    print(f"\nTotal required answer keys: {len(required_keys)}")
    print(f"Total points possible: {total_points:.1f}")
    
    # Group by category
    categories = {}
    for key, points in required_keys.items():
        category = key.split('_')[1]  # REG, MDT, AEX, CEX
        if category not in categories:
            categories[category] = {'count': 0, 'points': 0.0}
        categories[category]['count'] += 1
        categories[category]['points'] += points
    
    print("\nBreakdown by category:")
    for cat in sorted(categories.keys()):
        info = categories[cat]
        print(f"  {cat}: {info['count']} keys, {info['points']:.1f} points")
    
    print("\n" + "-" * 80)
    print("VERIFICATION RESULTS")
    print("-" * 80)
    
    if not missing and not extra:
        print("✓ All answer keys are present and correct!")
        print(f"✓ Coverage: {covered_points:.1f} / {total_points:.1f} points ({covered_points/total_points*100:.1f}%)")
    else:
        if missing:
            print(f"\n✗ Missing {len(missing)} answer keys:")
            for key in sorted(missing):
                points = required_keys[key]
                print(f"  - {key} ({points} points)")
            
            missing_points = sum(required_keys[k] for k in missing)
            print(f"\n  Total missing: {missing_points:.1f} points")
        
        if extra:
            print(f"\n⚠ Extra {len(extra)} answer keys (not in README):")
            for key in sorted(extra):
                print(f"  - {key}")
        
        print(f"\nCoverage: {covered_points:.1f} / {total_points:.1f} points ({covered_points/total_points*100:.1f}%)")
    
    print("\n" + "=" * 80)


def main():
    """Main function."""
    # Extract answer keys from README
    print("Extracting answer keys from README.md...")
    required_keys = extract_answer_keys_from_readme()
    
    # Load answer sheet
    print("Loading answer-sheet.yaml...")
    answer_sheet = load_answer_sheet()
    
    # Verify completeness
    missing, extra, total_points, covered_points = verify_completeness(
        required_keys, answer_sheet
    )
    
    # Print results
    print_results(required_keys, missing, extra, total_points, covered_points)
    
    # Export list of required keys
    print("\nExporting required keys to answer_keys_required.txt...")
    with open('answer_keys_required.txt', 'w') as f:
        f.write("# Required Answer Keys for Assignment A2\n")
        f.write(f"# Total: {len(required_keys)} keys, {total_points:.1f} points\n\n")
        
        for category in sorted(set(k.split('_')[1] for k in required_keys.keys())):
            f.write(f"\n## {category} Category\n")
            cat_keys = {k: v for k, v in required_keys.items() if k.split('_')[1] == category}
            for key in sorted(cat_keys.keys()):
                f.write(f"{key}: {cat_keys[key]} points\n")
    
    print("✓ Saved to answer_keys_required.txt")


if __name__ == '__main__':
    main()
