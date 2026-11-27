"""
Template for creating reproducible simulated datasets.

PRINCIPLES:
1. Seed control: Always use explicit random seed for reproducibility
2. Ground truth: Parameters should be interpretable (e.g., effect sizes, SDs)
3. Orthogonal variation: Decouple aspects (mean vs. variance, skew vs. kurtosis)
4. Validation: Include checks that the simulated data matches intentions
5. Parameterization: Every knob should have a clear interpretable meaning
"""

# KEY PARAMETERS (always do this first)
# ... your controllable knobs ...


def simulate(parameters):
    """Generate data with known, controllable properties."""
    # Step 1: Set seed for reproducibility
    # Step 2: Generate base distribution
    # Step 3: Add/modify distribution properties (skew, heterogeneity, etc.)
    # Step 4: Assemble into DataFrame with clear structure
    # Step 5: (Optional) Validate that simulated data has expected properties
    pass


# Optional: validation function
def validate_simulation(df):
    """Check that simulated data matches intention (e.g., expected effect size)."""
    pass
