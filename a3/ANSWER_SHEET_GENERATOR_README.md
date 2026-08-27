# Automatic Answer Sheet Generator

## Overview

The `generate_answer_sheet.py` script automatically extracts data from your repository files and generates a complete `answer-sheet.yaml` file for Assignment A3.

## Features

✅ **Automatic Data Extraction**:
- TLE data from `data/sgp4_reference/tle.txt`
- SGP4 orbit parameters from `data/sgp4_reference/orbit_propagation.npz`
- Euler integration results from `data/euler_outputs/dt100s_euler_output.txt`
- Velocity Verlet results from `data/verlet_outputs/dt100s_verlet_output.txt`
- CGPD analysis timesteps from `data/summary/cgpd_vs_timestep.npz`
- Timing measurements from output file headers
- Source code from Fortran and Python files
- Plot file paths automatically discovered

✅ **Complete Answer Sheet**:
- All mandatory (MDT) answers
- All regular (REG) answers
- Assignment excellence (AEX) section
- Code excellence (CEX) section
- AI use declaration
- Workload and feedback

✅ **Format Validation**:
- Generates valid YAML format
- Passes `answer-sheet-sanity.py` validation
- Preserves correct data types (floats, lists, strings)

## Usage

### Basic Usage

```bash
python3 generate_answer_sheet.py
```

This will:
1. Extract all data from repository files
2. Generate `answer-sheet.yaml` in the current directory
3. Display progress and completion status

### Step-by-Step Workflow

1. **Ensure your data is generated**:
   ```bash
   # Run SGP4 propagation (if not done)
   python3 src/python/propagator_sgp4.py
   
   # Run Euler propagation for dt=100s (if not done)
   ./scripts/run_propagation.sh 100
   
   # Run Verlet propagation for dt=100s (if not done)
   ./scripts/run_propagation_verlet.sh 100
   
   # Run CGPD analysis (if not done)
   ./scripts/run_cgpd_analysis.sh
   ```

2. **Generate answer sheet**:
   ```bash
   python3 generate_answer_sheet.py
   ```

3. **Validate the output**:
   ```bash
   python3 answer-sheet-sanity.py answer-sheet.yaml
   ```

4. **Review and customize**:
   - Open `answer-sheet.yaml` in your editor
   - Review observations, interpretations, and conclusions
   - Customize any answers as needed
   - Add any missing plot files

5. **Submit**:
   - Upload `answer-sheet.yaml` to the course platform

## What Gets Extracted

### From Data Files

| Source File | Extracted Data |
|------------|----------------|
| `data/sgp4_reference/tle.txt` | TLE lines for satellite |
| `data/sgp4_reference/orbit_propagation.npz` | SGP4 time domain, initial/final states |
| `data/euler_outputs/dt100s_euler_output.txt` | Euler timing, states |
| `data/verlet_outputs/dt100s_verlet_output.txt` | Verlet timing, states |
| `data/summary/cgpd_vs_timestep.npz` | Timestep list for CGPD analysis |

### From Source Files

| Source File | Usage |
|------------|-------|
| `src/fortran/gravity.f90` | Gravitational model code |
| `src/fortran/euler_method.f90` | Euler integrator code |
| `src/fortran/velocity_verlet.f90` | Verlet integrator code |
| `src/python/compute_position_difference.py` | Position difference computation |
| `src/python/plot_cgpd_vs_timestep.py` | CGPD plotting code |

### From Plots Directory

- Automatically discovers all plot files in `plots/`
- Organizes by category (summary, timestep_comparisons, etc.)
- Generates correct relative paths

## Customization

### Changing Default Timestep

By default, the script extracts data for `dt=100s`. To change this:

```python
# Edit generate_answer_sheet.py
euler_data = self.extract_euler_results(timestep=50)  # Change to 50s
verlet_data = self.extract_verlet_results(timestep=50)
```

### Modifying Text Answers

The script includes default text for observations, interpretations, and conclusions. To customize:

1. **Option 1**: Edit methods in the script:
   - `get_default_observations()`
   - `get_default_interpretations()`
   - `get_default_conclusions()`
   - `get_default_verlet_observations()`
   - `get_default_verlet_interpretations()`
   - `get_default_verlet_conclusions()`

2. **Option 2**: Edit the generated `answer-sheet.yaml` directly after running the script

### Adding Additional Data Sources

To extract from additional files:

```python
def extract_custom_data(self):
    """Extract from custom data file."""
    file_path = self.repo_root / "path/to/custom/file.txt"
    # Your extraction logic
    return extracted_data
```

Then add to `generate_answer_sheet()`:

```python
custom_data = self.extract_custom_data()
answers['ss_CUSTOM_KEY'] = custom_data
```

## Troubleshooting

### Error: File not found

**Problem**: Missing data files

**Solution**: Ensure all required propagations have been run:
```bash
./scripts/run_propagation.sh 100
./scripts/run_propagation_verlet.sh 100
./scripts/run_cgpd_analysis.sh
```

### Error: Invalid YAML format

**Problem**: Special characters in extracted text

**Solution**: The script handles YAML escaping automatically. If issues persist, check for unusual characters in source code comments.

### Warning: Missing plots

**Problem**: Expected plot files don't exist

**Solution**: Generate missing plots:
```bash
# For Keplerian plots
python3 src/python/plot_keplerian.py data/sgp4_reference/orbit_propagation.npz plots/sgp4

# For comparison plots
python3 src/python/compute_position_difference.py
```

## Requirements

- Python 3.6+
- NumPy
- PyYAML

Install dependencies:
```bash
pip install numpy pyyaml
```

## Advanced Usage

### Using as a Module

```python
from generate_answer_sheet import AnswerSheetGenerator

# Create generator
generator = AnswerSheetGenerator(repo_root="/path/to/repo")

# Generate answers dictionary
answers = generator.generate_answer_sheet()

# Access specific values
print(f"Euler integration time: {answers['sf_REG_EulerTimeTotal_NUM_0.5']}")

# Save with custom filename
generator.save_yaml("my-answers.yaml")
```

### Extracting Specific Data

```python
generator = AnswerSheetGenerator()

# Get just SGP4 data
sgp4_data = generator.load_sgp4_orbit()
print(f"Initial position: {sgp4_data['pos_initial']}")

# Get just Euler results
euler_data = generator.extract_euler_results(timestep=100)
print(f"Integration time: {euler_data['integration_time']}")
```

## File Structure Requirements

The generator expects this directory structure:

```
repo_root/
├── data/
│   ├── sgp4_reference/
│   │   ├── tle.txt
│   │   └── orbit_propagation.npz
│   ├── euler_outputs/
│   │   └── dt100s_euler_output.txt
│   ├── verlet_outputs/
│   │   └── dt100s_verlet_output.txt
│   └── summary/
│       └── cgpd_vs_timestep.npz
├── src/
│   ├── fortran/
│   │   ├── gravity.f90
│   │   ├── euler_method.f90
│   │   └── velocity_verlet.f90
│   └── python/
│       ├── compute_position_difference.py
│       └── plot_cgpd_vs_timestep.py
└── plots/
    ├── summary/
    └── timestep_comparisons/
```

## Output Format

The generated `answer-sheet.yaml` follows the assignment specification:

```yaml
# Assignment A3 Answer Sheet
# Practical Astrodynamics
# Auto-generated from repository data

ss_REG_Language_GEN_0: "Fortran 90/95 for numerical integration, Python 3..."
ls_MDT_TLE_GEN_0:
  - "USA 149 (DSP 20)"
  - "1 26356U 00024A   25329.33616394 ..."
  - "2 26356  13.0157 ..."
sf_MDT_OrbTimeIni_NUM_0: 0.0
# ... etc
```

## Version History

- **v1.0** (2024-11-26): Initial release
  - Automatic data extraction from all sources
  - Complete answer sheet generation
  - Validation support

## Contributing

To improve the generator:

1. Add new extraction methods for additional data sources
2. Improve text generation for observations/conclusions
3. Add error handling for missing files
4. Support for multiple satellite configurations

## License

This script is part of the Assignment A3 submission tools.
