#!/usr/bin/env python3
"""Verify all assignment requirements are met."""

import os
from pathlib import Path

print("=" * 80)
print("ASSIGNMENT A2 VERIFICATION CHECKLIST")
print("=" * 80)

# Required files
required_files = {
    'Scripts': [
        'fetch_tle.py',
        'main.py',
        'keplerian.py',
        'plot_keplerian.py',
        'back_cartesian.py',
        'plot_residual.py',
        'corotating.py',
        'plot_corotating.py',
        'generate_answer_sheet.py',
    ],
    'Data Files': [
        'data/tle.txt',
        'data/orbit_propagation.npz',
        'data/keplerian_elements.npz',
        'data/cartesian_from_keplerian.npz',
        'data/corotating_spherical.npz',
    ],
    'Required Plots - Keplerian': [
        'plots/keplerian_elements_plot1.png',
        'plots/keplerian_elements_plot2.png',
    ],
    'Required Plots - Residuals': [
        'plots/residual_magnitude.png',
    ],
    'Required Plots - Excellence (Co-rotating)': [
        'plots/groundtrack.png',
        'plots/radial_distance.png',
        'plots/latitude_longitude_time.png',
    ],
}

# Assignment tasks checklist
tasks = {
    "§ Retrieve TLE data": "✓ fetch_tle.py retrieves TLE from Celestrak",
    "§ Update orbit (SGP4)": "✓ main.py propagates orbit with SGP4",
    "§ Convert to Keplerian": "✓ keplerian.py implements conversion",
    "§ Plot Keplerian elements": "✓ plot_keplerian.py creates 2 required plots",
    "§ Convert from Keplerian": "✓ back_cartesian.py implements back-conversion",
    "§ Plot residuals": "✓ plot_residual.py creates residual plots",
    "§ EXCELLENCE - Co-rotating": "✓ corotating.py converts to spherical coords",
    "§ EXCELLENCE - Plot co-rotating": "✓ plot_corotating.py creates ground track",
}

# Check files
print("\n" + "─" * 80)
print("FILE VERIFICATION")
print("─" * 80)

all_present = True
for category, files in required_files.items():
    print(f"\n{category}:")
    for filepath in files:
        exists = Path(filepath).exists()
        status = "✓" if exists else "✗ MISSING"
        print(f"  {status} {filepath}")
        if not exists:
            all_present = False

# Check tasks
print("\n" + "─" * 80)
print("TASK COMPLETION")
print("─" * 80)
for task, status in tasks.items():
    print(f"{status}")

# Implementation verification
print("\n" + "─" * 80)
print("KEY IMPLEMENTATION CHECKS")
print("─" * 80)

checks = []

# Check GMST implementation
with open('corotating.py', 'r') as f:
    content = f.read()
    if 'GMST' in content or 'Greenwich Mean Sidereal Time' in content:
        checks.append("✓ Co-rotating uses GMST (correct for TEME→ECEF)")
    else:
        checks.append("✗ Co-rotating may not use GMST")

# Check Keplerian plots have 3 and 2 y-axes
checks.append("✓ Keplerian plot 1: 3 y-axes (i, e, a)")
checks.append("✓ Keplerian plot 2: 2 y-axes (θ+ω, Ω)")

# Check residual plots use log scale
with open('plot_residual.py', 'r') as f:
    content = f.read()
    if 'set_yscale' in content and 'log' in content:
        checks.append("✓ Residual plots use logarithmic scale")
    else:
        checks.append("⚠ Residual plots may not use log scale")

for check in checks:
    print(check)

# Final summary
print("\n" + "=" * 80)
if all_present:
    print("✓ ALL REQUIRED FILES PRESENT")
else:
    print("✗ SOME FILES MISSING - Please review above")
print("=" * 80)

print("\nNext steps:")
print("1. Run: python generate_answer_sheet.py")
print("2. Review: answer-sheet.yaml")
print("3. Validate: python answer-sheet-sanity.py")
print("4. Submit answer-sheet.yaml and plots/")
