#!/usr/bin/env python3
"""Configuration loader for Assignment A2.

Loads configuration from config.yaml and provides type-safe access to parameters.
This implements Code Excellence by separating configuration from code.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PhysicsConfig:
    """Physical constants."""
    mu_earth: float
    omega_earth: float
    r_earth: float


@dataclass
class PropagationConfig:
    """Orbit propagation parameters."""
    initial_time_seconds: float
    final_time_seconds: float
    time_step_seconds: float


@dataclass
class SatelliteConfig:
    """Satellite configuration."""
    norad_id: int
    celestrak_catalog: str


@dataclass
class PathsConfig:
    """File paths."""
    data_dir: str
    plots_dir: str
    tle_file: str
    orbit_propagation: str
    keplerian_elements: str
    cartesian_from_keplerian: str
    corotating_spherical: str


@dataclass
class PlottingConfig:
    """Plotting parameters."""
    dpi: int
    figsize_standard: list
    figsize_wide: list
    figsize_keplerian: list
    skip_if_exists: bool
    style: str
    grid_alpha: float
    line_width: float


@dataclass
class TolerancesConfig:
    """Numerical tolerances."""
    eccentricity_circular: float
    inclination_equatorial: float
    position_tolerance_km: float
    velocity_tolerance_km_s: float
    angle_tolerance_deg: float


@dataclass
class DebugConfig:
    """Debug settings."""
    enabled: bool
    verbose: bool
    save_intermediate: bool


@dataclass
class FeaturesConfig:
    """Code excellence features."""
    auto_create_directories: bool
    auto_download_tle: bool
    validate_inputs: bool
    benchmark_performance: bool
    unit_tests: bool


class Config:
    """Main configuration class providing type-safe access to all parameters."""
    
    def __init__(self, config_file: str = "config.yaml"):
        """Load configuration from YAML file.
        
        Args:
            config_file: Path to configuration YAML file
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Load each configuration section
        self.physics = PhysicsConfig(**data['physics'])
        self.propagation = PropagationConfig(**data['propagation'])
        self.satellite = SatelliteConfig(**data['satellite'])
        self.paths = PathsConfig(**data['paths'])
        self.plotting = PlottingConfig(**data['plotting'])
        self.tolerances = TolerancesConfig(**data['tolerances'])
        self.debug = DebugConfig(**data['debug'])
        self.features = FeaturesConfig(**data['features'])
    
    def __repr__(self) -> str:
        return f"Config(physics={self.physics}, propagation={self.propagation})"


# Global configuration instance
_config: Optional[Config] = None


def load_config(config_file: str = "config.yaml") -> Config:
    """Load or return cached configuration.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Config object with all parameters
    """
    global _config
    if _config is None:
        _config = Config(config_file)
    return _config


def get_config() -> Config:
    """Get current configuration (loads default if not yet loaded).
    
    Returns:
        Config object
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


if __name__ == "__main__":
    # Test configuration loading
    config = load_config()
    print("Configuration loaded successfully!")
    print(f"\nPhysics: {config.physics}")
    print(f"Propagation: {config.propagation}")
    print(f"Satellite: {config.satellite}")
    print(f"Tolerances: {config.tolerances}")
