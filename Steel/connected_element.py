import numpy as np
import pandas as pd
import seaborn as sns
import math
import sympy
import pint

# Create a unit registry
ureg = pint.UnitRegistry()

def connected_elem_shear_yield_str(design_method, part1_t, part1_len, part1_yield, part2_t, part2_len, part2_yield):
    """
    Calculates the nominal shear yield strength of connected elements (plates or members)
    based on the design method (ASD or LRFD).

    Args:
        design_method (str): The design method, either "ASD" (Allowable Stress Design) 
                              or "LRFD" (Load and Resistance Factor Design).
        part1_t (pint.Quantity): Thickness of part 1 (plate or member) with units.
        part1_len (pint.Quantity): Length of part 1 (along the shear plane) with units.
        part1_yield (pint.Quantity): Yield strength of part 1 material with units.
        part2_t (pint.Quantity): Thickness of part 2 with units.
        part2_len (pint.Quantity): Length of part 2 (along the shear plane) with units.
        part2_yield (pint.Quantity): Yield strength of part 2 material with units.

    Returns:
        tuple: A tuple containing two `pint.Quantity` objects:
            - The allowable shear yield strength of part 1.
            - The allowable shear yield strength of part 2.
    """

    # Ensure consistent units
    part1_t = part1_t.to('inch')
    part1_len = part1_len.to('inch')
    part1_yield = part1_yield.to('ksi')
    part2_t = part2_t.to('inch')
    part2_len = part2_len.to('inch')
    part2_yield = part2_yield.to('ksi')

    # Calculate the nominal shear yield strength (Rn) for both parts
    # 0.60: Reduction factor for shear yield strength
    r_n1 = 0.60 * part1_yield * (part1_t * part1_len)
    r_n2 = 0.60 * part2_yield * (part2_t * part2_len)

    if design_method == "ASD":
        # ASD: Apply a factor of safety (FOS)
        fos = 1.50  
        return r_n1 / fos, r_n2 / fos

    elif design_method == "LRFD":
        # LRFD: Apply a strength reduction factor (phi)
        str_reduction = 1.00  
        return str_reduction * r_n1, str_reduction * r_n2

    else:
        raise ValueError("Invalid design method. Use 'ASD' or 'LRFD'.")
    

def connected_elem_shear_rupture_str(design_method, bolt_dia, bolt_count, 
                                     part1_t, part1_len, part1_ult, part2_t, part2_len, part2_ult):
    """
    Calculates the nominal shear rupture strength of connected elements (plates or members)
    based on the design method (ASD or LRFD).

    Args:
        design_method (str): The design method, either "ASD" (Allowable Stress Design) 
                              or "LRFD" (Load and Resistance Factor Design).
        bolt_dia (pint.Quantity): The diameter of the bolts with units.
        bolt_count (int): The number of bolts in the connection.
        part1_t (pint.Quantity): Thickness of part 1 with units.
        part1_len (pint.Quantity): Length of part 1 (along the shear plane) with units.
        part1_ult (pint.Quantity): Ultimate tensile strength of part 1 material with units.
        part2_t (pint.Quantity): Thickness of part 2 with units.
        part2_len (pint.Quantity): Length of part 2 (along the shear plane) with units.
        part2_ult (pint.Quantity): Ultimate tensile strength of part 2 material with units.

    Returns:
        tuple: A tuple containing two `pint.Quantity` objects:
            - The allowable shear rupture strength of part 1.
            - The allowable shear rupture strength of part 2.
    """

    # Ensure consistent units
    bolt_dia = bolt_dia.to('inch')
    part1_t = part1_t.to('inch')
    part1_len = part1_len.to('inch')
    part1_ult = part1_ult.to('ksi')
    part2_t = part2_t.to('inch')
    part2_len = part2_len.to('inch')
    part2_ult = part2_ult.to('ksi')

    # Calculate the net shear area for both parts, considering bolt holes
    # 0.063 inch: Assumed bolt hole clearance (adjust if needed)
    net_width_1 = part1_len - (bolt_dia + 0.063 * ureg.inch) * bolt_count
    net_width_2 = part2_len - (bolt_dia + 0.063 * ureg.inch) * bolt_count

    a_nv1 = part1_t * net_width_1
    a_nv2 = part2_t * net_width_2

    # Calculate nominal shear rupture strengths (Rn) for both parts
    # 0.60: Reduction factor for shear rupture strength
    r_n1 = 0.60 * part1_ult * a_nv1
    r_n2 = 0.60 * part2_ult * a_nv2

    if design_method == "ASD":
        # ASD: Apply a factor of safety (FOS)
        fos = 2.00  
        return r_n1 / fos, r_n2 / fos

    elif design_method == "LRFD":
        # LRFD: Apply a strength reduction factor (phi)
        str_reduction = 0.75  
        return str_reduction * r_n1, str_reduction * r_n2

    else:
        raise ValueError("Invalid design method. Use 'ASD' or 'LRFD'.")
    

def connected_elem_tensile_yield_str(design_method, part1_t, part1_len, part1_yield, part2_t, part2_len, part2_yield):
    """
    Calculates the nominal tensile yield strength of connected elements (plates or members)
    based on the design method (ASD or LRFD).

    Args:
        design_method (str): The design method, either "ASD" (Allowable Stress Design) 
                              or "LRFD" (Load and Resistance Factor Design).
        part1_t (pint.Quantity): Thickness of part 1 with units.
        part1_len (pint.Quantity): Width of part 1 (perpendicular to the tensile force) with units.
        part1_yield (pint.Quantity): Yield strength of part 1 material with units.
        part2_t (pint.Quantity): Thickness of part 2 with units.
        part2_len (pint.Quantity): Width of part 2 (perpendicular to the tensile force) with units.
        part2_yield (pint.Quantity): Yield strength of part 2 material with units.

    Returns:
        tuple: A tuple containing two `pint.Quantity` objects:
            - The allowable tensile yield strength of part 1.
            - The allowable tensile yield strength of part 2.
    """

    # Ensure consistent units
    part1_t = part1_t.to('inch')
    part1_len = part1_len.to('inch')
    part1_yield = part1_yield.to('ksi')
    part2_t = part2_t.to('inch')
    part2_len = part2_len.to('inch')
    part2_yield = part2_yield.to('ksi')

    # Calculate the nominal tensile yield strength (Rn) for both parts
    r_n1 = part1_yield * (part1_t * part1_len)  # Yield strength * Area
    r_n2 = part2_yield * (part2_t * part2_len)

    if design_method == "ASD":
        # ASD: Apply a factor of safety (FOS) of 1.67
        fos = 1.67  
        return r_n1 / fos, r_n2 / fos

    elif design_method == "LRFD":
        # LRFD: Apply a strength reduction factor (phi) of 0.90
        str_reduction = 0.90  
        return str_reduction * r_n1, str_reduction * r_n2

    else:
        raise ValueError("Invalid design method. Use 'ASD' or 'LRFD'.")
    


def connected_elem_tensile_rupture_str(design_method, bolt_dia, bolt_count, shear_lag, 
                                       part1_t, part1_len, part1_ult, part2_t, part2_len, part2_ult):
    """
    Calculates the nominal tensile rupture strength of connected elements (plates or members)
    based on the design method (ASD or LRFD), considering the effect of shear lag.

    Args:
        design_method (str): The design method, either "ASD" (Allowable Stress Design) 
                              or "LRFD" (Load and Resistance Factor Design).
        bolt_dia (pint.Quantity): The diameter of the bolts with units.
        bolt_count (int): The number of bolts in the connection.
        shear_lag (float): The shear lag factor (between 0 and 1) to account for 
                           non-uniform stress distribution due to the connection.
        part1_t (pint.Quantity): Thickness of part 1 with units.
        part1_len (pint.Quantity): Width of part 1 (perpendicular to the tensile force) with units.
        part1_ult (pint.Quantity): Ultimate tensile strength of part 1 material with units.
        part2_t (pint.Quantity): Thickness of part 2 with units.
        part2_len (pint.Quantity): Width of part 2 (perpendicular to the tensile force) with units.
        part2_ult (pint.Quantity): Ultimate tensile strength of part 2 material with units.

    Returns:
        tuple: A tuple containing two `pint.Quantity` objects:
            - The allowable tensile rupture strength of part 1.
            - The allowable tensile rupture strength of part 2.
    """

    # Ensure consistent units
    bolt_dia = bolt_dia.to('inch')
    part1_t = part1_t.to('inch')
    part1_len = part1_len.to('inch')
    part1_ult = part1_ult.to('ksi')
    part2_t = part2_t.to('inch')
    part2_len = part2_len.to('inch')
    part2_ult = part2_ult.to('ksi')

    # Calculate the net width for both parts, considering bolt holes
    # 0.063 inch: Assumed bolt hole clearance (adjust if needed)
    net_width_1 = part1_len - (bolt_dia + 0.063 * ureg.inch) * bolt_count
    net_width_2 = part2_len - (bolt_dia + 0.063 * ureg.inch) * bolt_count

    # Calculate net areas
    a_nv1 = part1_t * net_width_1
    a_nv2 = part2_t * net_width_2

    # Calculate nominal tensile rupture strengths (Rn) for both parts, incorporating shear lag
    r_n1 = part1_ult * a_nv1 * shear_lag
    r_n2 = part2_ult * a_nv2 * shear_lag

    if design_method == "ASD":
        # ASD: Apply a factor of safety (FOS) - typically 2.0 for tensile rupture
        fos = 2.00  
        return r_n1 / fos, r_n2 / fos

    elif design_method == "LRFD":
        # LRFD: Apply a strength reduction factor (phi) - typically 0.75 for tensile rupture
        str_reduction = 0.75  
        return str_reduction * r_n1, str_reduction * r_n2

    else:
        raise ValueError("Invalid design method. Use 'ASD' or 'LRFD'.")