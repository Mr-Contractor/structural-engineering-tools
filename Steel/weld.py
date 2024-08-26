import numpy as np
import pandas as pd
import seaborn as sns
import math
import sympy
import pint

# Create a unit registry
ureg = pint.UnitRegistry()

def min_weld_size(part1_t, part2_t):
    """
    Calculates the minimum weld size based on the thickness of two parts.

    Args:
        part1_t (pint.Quantity): Thickness of part 1 in inches.
        part2_t (pint.Quantity): Thickness of part 2 in inches.

    Returns:
        pint.Quantity: The minimum weld size in inches.
    """

    # Ensure inputs have units of inches
    part1_t = part1_t.to(ureg.inch)
    part2_t = part2_t.to(ureg.inch)

    t_min = min(part1_t, part2_t)

    if t_min < 0.25 * ureg.inch:
        return 0.1250
    elif 0.25 * ureg.inch <= t_min < 0.5 * ureg.inch:
        return 0.1875
    elif 0.5 * ureg.inch <= t_min < 0.75 * ureg.inch:
        return 0.2500
    elif 0.75 * ureg.inch <= t_min:
        return 0.3125


def weld_material_strength(design_method, weld_size, weld_length, weld_sides):
    """
    Calculates the nominal weld strength based on the design method (ASD or LRFD).

    Args:
        design_method (str): The design method, either "ASD" (Allowable Stress Design) 
                              or "LRFD" (Load and Resistance Factor Design).
        weld_size (float): The size of the weld in sixteenths of an inch (e.g., 2, 3, 4, etc.).
        weld_length (pint.Quantity): The length of the weld with units (e.g., 6 * ureg.inch).
        weld_sides (int): The number of sides the weld is applied to (1 or 2).

    Returns:
        pint.Quantity: The allowable weld strength with units (e.g., kip).
    """

    # Ensure weld_length has units of inches
    weld_length = weld_length.to(ureg.inch)

    # Calculate the nominal strength of the weld (Rn)
    # 0.60: Reduction factor for fillet welds
    # 70 ksi: Assumed electrode strength (common for E70 electrodes)
    # math.sqrt(2)/2: Throat thickness factor for 45-degree fillet welds
    # (weld_size/16): Convert weld size from fractions to decimals
    r_n = 0.60 * (70 * ureg.ksi) * (math.sqrt(2) / 2) * ((weld_size / 16) * ureg.inch) * weld_length * weld_sides

    if design_method == "ASD":
        # ASD: Apply a factor of safety (FOS)
        fos = 2.00
        return r_n / fos

    elif design_method == "LRFD":
        # LRFD: Apply a strength reduction factor (phi)
        str_reduction = 0.75
        return str_reduction * r_n

    else:
        raise ValueError("Invalid design method. Use 'ASD' or 'LRFD'.")



def weld_rupture_strength(design_method, weld_size, weld_length, weld_sides, 
                          part1_t, part1_ult, part2_t, part2_ult):
    """
    Calculates the weld rupture strength considering base metal strength.

    Args:
        design_method (str): Design method ("ASD" or "LRFD").
        weld_size (float): Weld size in sixteenths of an inch.
        weld_length (pint.Quantity): Weld length with units (e.g., 6 * ureg.inch).
        weld_sides (int): Number of sides welded (1 or 2).
        part1_t (pint.Quantity): Thickness of part 1 with units.
        part1_ult (pint.Quantity): Ultimate tensile strength of part 1 with units.
        part2_t (pint.Quantity): Thickness of part 2 with units.
        part2_ult (pint.Quantity): Ultimate tensile strength of part 2 with units.

    Returns:
        pint.Quantity: Weld rupture strength considering base metal, with units.
    """

    # Ensure consistent units
    weld_length = weld_length.to(ureg.inch)
    part1_t = part1_t.to(ureg.inch)
    part2_t = part2_t.to(ureg.inch)
    part1_ult = part1_ult.to(ureg.ksi)
    part2_ult = part2_ult.to(ureg.ksi)

    # Calculate weld throat area and strength
    throat_area = 0.707 * (weld_size / 16) * ureg.inch  # 0.707 for 45-degree fillet
    weld_strength_per_length = 0.60 * 70 * ureg.ksi * throat_area

    # Calculate minimum thicknesses for base metal rupture
    if weld_sides == 1:
        t1_min = weld_strength_per_length / (0.6 * part1_ult)
        t2_min = weld_strength_per_length / (0.6 * part2_ult)
    elif weld_sides == 2:
        t1_min = 2 * weld_strength_per_length / (0.6 * part1_ult)
        t2_min = 2 * weld_strength_per_length / (0.6 * part2_ult)

    # Calculate reduction factors based on base metal thicknesses
    reduction_1 = part1_t / t1_min
    reduction_2 = part2_t / t2_min

    # Get weld strength based on design method
    weld_mat_strength = weld_material_strength(design_method, weld_size, weld_length, weld_sides)

    # Return reduced strength if base metal governs
    if reduction_1 < 1 or reduction_2 < 1:
        return weld_mat_strength * min(reduction_1, reduction_2)
    else:
        return weld_mat_strength
    
