import numpy as np
import pandas as pd
import seaborn as sns
import math
import sympy
import pint

# Create a unit registry
ureg = pint.UnitRegistry()

def nominal_fastener_strength(f_u):
    """
    Calculates the nominal shear and tensile strengths of a fastener based on its ultimate tensile strength.

    Args:
        f_u (pint.Quantity): The ultimate tensile strength of the fastener material with units (e.g., ksi).

    Returns:
        tuple: A tuple containing two `pint.Quantity` objects:
            - f_nv: The nominal shear strength of the fastener.
            - f_nt: The nominal tensile strength of the fastener.
    """

    # Ensure f_u has units of ksi (kips per square inch)
    f_u = f_u.to('ksi')  

    # Calculate nominal shear strength (Fnv) using a reduction factor of 0.45
    f_nv = 0.45 * f_u

    # Calculate nominal tensile strength (Fnt) using a reduction factor of 0.75
    f_nt = 0.75 * f_u

    return f_nv, f_nt


def shear_strength_bolts(design_method, bolt_dia, f_u):
    """
    Calculates the nominal shear strength of bolts based on the design method (ASD or LRFD).

    Args:
        design_method (str): The design method, either "ASD" (Allowable Stress Design) 
                              or "LRFD" (Load and Resistance Factor Design).
        bolt_dia (pint.Quantity): The diameter of the bolt with units (e.g., 0.5 * ureg.inch).
        f_u (pint.Quantity): The ultimate tensile strength of the bolt material with units (e.g., 120 * ureg.ksi).

    Returns:
        pint.Quantity: The allowable shear strength of the bolt with units.
    """

    # Get nominal shear and tensile strengths from the helper function
    f_nv, _ = nominal_fastener_strength(f_u)  # We only need the shear strength (f_nv)

    # Ensure bolt_dia has units of inches
    bolt_dia = bolt_dia.to('inch')

    # Calculate the nominal shear strength of the bolt (Rn)
    # f_nv: Nominal shear strength from material properties
    # (math.pi/4) * (bolt_dia**2): Cross-sectional area of the bolt
    r_n = f_nv * (math.pi / 4) * (bolt_dia ** 2)

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
    


def bearing_strength_bolts(design_method, bolt_dia, part1_t, part1_ult, part2_t, part2_ult):
    """
    Calculates the nominal bearing strength of bolts on connected parts 
    based on the design method (ASD or LRFD).

    Args:
        design_method (str): The design method, either "ASD" (Allowable Stress Design) 
                              or "LRFD" (Load and Resistance Factor Design).
        bolt_dia (pint.Quantity): The diameter of the bolt with units (e.g., 0.5 * ureg.inch).
        part1_t (pint.Quantity): Thickness of part 1 with units.
        part1_ult (pint.Quantity): Ultimate tensile strength of part 1 with units.
        part2_t (pint.Quantity): Thickness of part 2 with units.
        part2_ult (pint.Quantity): Ultimate tensile strength of part 2 with units.

    Returns:
        tuple: A tuple containing two `pint.Quantity` objects:
            - The allowable bearing strength on part 1.
            - The allowable bearing strength on part 2.
    """

    # Ensure consistent units
    bolt_dia = bolt_dia.to('inch')
    part1_t = part1_t.to('inch')
    part2_t = part2_t.to('inch')
    part1_ult = part1_ult.to('ksi')
    part2_ult = part2_ult.to('ksi')

    # Calculate nominal bearing strengths (Rn) for both parts
    # 2.4: Bearing strength factor 
    r_n1 = 2.4 * bolt_dia * part1_t * part1_ult
    r_n2 = 2.4 * bolt_dia * part2_t * part2_ult

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


def tearout_strength_bolts(design_method, bolt_dia, 
                           part1_edge_dist, part2_edge_dist, 
                           part1_t, part1_ult, part2_t, part2_ult):
    """
    Calculates the nominal tearout strength of bolts on connected parts 
    based on the design method (ASD or LRFD).

    Args:
        design_method (str): The design method, either "ASD" (Allowable Stress Design) 
                              or "LRFD" (Load and Resistance Factor Design).
        bolt_dia (pint.Quantity): The diameter of the bolt with units (e.g., 0.5 * ureg.inch).
        part1_edge_dist (pint.Quantity): Distance from the bolt center to the edge of part 1 with units.
        part2_edge_dist (pint.Quantity): Distance from the bolt center to the edge of part 2 with units.
        part1_t (pint.Quantity): Thickness of part 1 with units.
        part1_ult (pint.Quantity): Ultimate tensile strength of part 1 with units.
        part2_t (pint.Quantity): Thickness of part 2 with units.
        part2_ult (pint.Quantity): Ultimate tensile strength of part 2 with units.

    Returns:
        tuple: A tuple containing two `pint.Quantity` objects:
            - The allowable tearout strength on part 1.
            - The allowable tearout strength on part 2.
    """

    # Ensure consistent units
    bolt_dia = bolt_dia.to('inch')
    part1_edge_dist = part1_edge_dist.to('inch')
    part2_edge_dist = part2_edge_dist.to('inch')
    part1_t = part1_t.to('inch')
    part2_t = part2_t.to('inch')
    part1_ult = part1_ult.to('ksi')
    part2_ult = part2_ult.to('ksi')

    # Calculate the net distance from the bolt edge to the part edge for both parts
    net_dist_1 = part1_edge_dist - ((bolt_dia + 0.125 * ureg.inch)/2)
    net_dist_2 = part2_edge_dist - ((bolt_dia + 0.125 * ureg.inch)/2)

    # Calculate nominal tearout strengths (Rn) for both parts
    # 1.2: Tearout strength factor
    r_n1 = 1.2 * net_dist_1 * part1_t * part1_ult
    r_n2 = 1.2 * net_dist_2 * part2_t * part2_ult

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
    

def tensile_strength_bolts(design_method, bolt_dia, f_u):
    """
    Calculates the nominal tensile strength of bolts based on the design method (ASD or LRFD).

    Args:
        design_method (str): The design method, either "ASD" (Allowable Stress Design) 
                              or "LRFD" (Load and Resistance Factor Design).
        bolt_dia (pint.Quantity): The diameter of the bolt with units (e.g., 0.5 * ureg.inch).
        f_u (pint.Quantity): The ultimate tensile strength of the bolt material with units (e.g., 120 * ureg.ksi).

    Returns:
        pint.Quantity: The allowable shear strength of the bolt with units.
    """

    # Get nominal shear and tensile strengths from the helper function
    _ , f_nt = nominal_fastener_strength(f_u)  # We only need the tensile strength (f_nt)

    # Ensure bolt_dia has units of inches
    bolt_dia = bolt_dia.to('inch')

    # Calculate the nominal shear strength of the bolt (Rn)
    # f_nv: Nominal shear strength from material properties
    # (math.pi/4) * (bolt_dia**2): Cross-sectional area of the bolt
    r_n = f_nt * (math.pi / 4) * (bolt_dia ** 2)

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
    