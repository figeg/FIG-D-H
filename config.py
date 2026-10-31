import calendar
from datetime import timedelta # Added this import
import pandas as pd

# --- COMPANY-SPECIFIC CONFIGURATIONS ---
# Define rules for each company.
# Each company can have default rules, location-specific overrides, and employee-specific overrides.
# calendar module constants (0=Monday, 6=Sunday)
COMPANY_CONFIGS = {
    "Al-hadabah times": {
        "default_rules": {
            "standard_shift_hours": 8,
            "short_t_threshold_hours": 7.5, # Employee is "missing" if total shift < this
            "more_t_start_hours": 9,        # More_T is calculated for hours > this
            "more_t_enabled": True,        # Global flag for More_T calculation for this company/location/employee
            "is_rotational_off": False,       # Default for fixed shifts
            "weekend_days": [calendar.FRIDAY], # Default for Al-hadabah if no specific location rule, assuming 1 Friday
            "fixed_break_deduction_minutes": 0, # Default to 0, no fixed break
            "fixed_break_threshold_hours": 0 # Default to 0, no fixed break threshold
        },
        "location_rules": { # Rules specific to `Source_Name` (derived from filename/device)
            "HO": {
                "weekend_days": [calendar.FRIDAY, calendar.SATURDAY], # These are potential weekend days for alternating rule
                "weekend_rule_type": "alternating_f_fs", # Specific rule for alternating weekends (F then F+S)
                "more_t_enabled": False,
                "is_rotational_off": False
            },
            "Warehouse": {"weekend_days": [calendar.FRIDAY], "is_rotational_off": False},
            "lighting plus": {"weekend_days": [calendar.FRIDAY], "more_t_enabled": False, "is_rotational_off": False},
            "S16": {"weekend_days": [calendar.FRIDAY], "more_t_enabled": False, "is_rotational_off": False},
            "S17": {"weekend_days": [calendar.FRIDAY], "more_t_enabled": False, "is_rotational_off": False},
            "S20": {"weekend_days": [calendar.FRIDAY], "more_t_enabled": False, "is_rotational_off": False},
            "S21": {"weekend_days": [calendar.FRIDAY], "more_t_enabled": False, "is_rotational_off": False},
            "S33": {"weekend_days": [calendar.FRIDAY], "more_t_start_hours": 8, "more_t_enabled": True, "is_rotational_off": False}, # Work all week
            "S14": {"weekend_days": [], "more_t_start_hours": 8, "more_t_enabled": True, "is_rotational_off": False}, # Work all week
            "S39": {"weekend_days": [], "more_t_start_hours": 8, "more_t_enabled": True, "is_rotational_off": False}, # Work all week
            "S40": {"weekend_days": [], "more_t_start_hours": 8, "more_t_enabled": True, "is_rotational_off": False}, # Work all week
            "S41": {"weekend_days": [], "more_t_start_hours": 8, "more_t_enabled": True, "is_rotational_off": False}, # Work all week
            "S42": {"weekend_days": [], "more_t_start_hours": 8, "more_t_enabled": True, "is_rotational_off": False}, # Work all week
            "Al hadabah Drivers": {"weekend_days": [], "more_t_start_hours": 8, "more_t_enabled": True, "is_rotational_off": False}, # Work all week
        }
    },
    "D&H": {
        "default_rules": {
            "standard_shift_hours": 8,
            "short_t_threshold_hours": 7.5,
            "more_t_start_hours": 9,
            "more_t_enabled": True,
            "weekend_days": [calendar.FRIDAY], # Default for D&H
            "is_rotational_off": False,
            "fixed_break_deduction_minutes": 0, # Default to 0, no fixed break
            "fixed_break_threshold_hours": 0 # Default to 0, no fixed break threshold
        },
        "employee_overrides": { # Rules specific to employee 'No.' (for Brand Managers)
            # These are Brand Managers who can have rotational offs and no More_T
            "1031": {"more_t_enabled": False, "is_rotational_off": True, "weekend_days": [], "rotational_days_off_per_week": 1}, # Ali Dagher (D&H)
            "12299": {"more_t_enabled": False, "is_rotational_off": True, "weekend_days": [], "rotational_days_off_per_week": 1}, # Fata (D&H)
            "2579": {"more_t_enabled": False, "is_rotational_off": True, "weekend_days": [], "rotational_days_off_per_week": 1},  # Aline Armani (D&H)
            "1494": {"more_t_enabled": False, "is_rotational_off": True, "weekend_days": [], "rotational_days_off_per_week": 1}, # Raeda (D&H)
            "1483": {"more_t_enabled": False, "is_rotational_off": True, "weekend_days": [], "rotational_days_off_per_week": 1}  # Mayada Abou (D&H)
        },
        "location_rules": {
            "HO": {"weekend_days": [calendar.FRIDAY], "is_rotational_off": False},
            "Warehouse": {"weekend_days": [calendar.FRIDAY], "is_rotational_off": False}
        }
    },
    "D&co": {
        "default_rules": {
            "standard_shift_hours": 8,
            "short_t_threshold_hours": 7.5,
            "more_t_start_hours": 9,
            "more_t_enabled": True,
            "weekend_days": [calendar.FRIDAY], # Default for D&co
            "is_rotational_off": False,
            "fixed_break_deduction_minutes": 0, # Default to 0, no fixed break
            "fixed_break_threshold_hours": 0 # Default to 0, no fixed break threshold
        },
        "employee_overrides": {
            # No specific employee overrides for D&co now as BMs moved to D&H
        },
        "location_rules": {
            "DCO HO": {"weekend_days": [calendar.FRIDAY], "is_rotational_off": False},
            "Warehouse": {"weekend_days": [calendar.FRIDAY], "is_rotational_off": False},
            # "Fashion SHW": {"weekend_days": [calendar.FRIDAY], "is_rotational_off": True, "rotational_days_off_per_week": 1},
        }
    },
    "D&CO Jordan": { # Same rules as D&co; locations are added via the Store Management page
        "default_rules": {
            "standard_shift_hours": 8,
            "short_t_threshold_hours": 7.5,
            "more_t_start_hours": 9,
            "more_t_enabled": True,
            "weekend_days": [calendar.FRIDAY],
            "is_rotational_off": False,
            "fixed_break_deduction_minutes": 0,
            "fixed_break_threshold_hours": 0
        },
        "employee_overrides": {},
        "location_rules": {}
    },
    "Second Cup": { # Added as a top-level company based on provided data
        "default_rules": {
            "standard_shift_hours": 9,
            "short_t_threshold_hours": 8.5,
            "more_t_start_hours": 10, # Default opening hours for general Second Cup locations
            "more_t_enabled": True,
            "weekend_days": [], # Based on "Only Fridays" # the weekend rotaion to be edited for each location
            "is_rotational_off": False,
            "opening_hours_count" : 12, # Default to 9 hours for general Second Cup
            "fixed_break_deduction_minutes": 0, # Set to 0 for Second Cup as per user's request: "2 punches days has no breaks"
            "fixed_break_threshold_hours": 0 # Not relevant if fixed_break_deduction_minutes is 0
        },
        "location_rules": {
            "2nd cup Warehouse": {"weekend_days": [calendar.FRIDAY], "is_rotational_off": False},
            # 24-hour locations with specific rules
            "Dar al Shifa": {
                "weekend_days": [],
                "is_rotational_off": True,
                "opening_hours_count": 24,
                "is_24_hour_location": True # Flag to trigger 24-hour specific logic
            },
            "Dar al Shifa Clinic": {
                "weekend_days": [],
                "is_rotational_off": True,
                "opening_hours_count": 24,
                "is_24_hour_location": True
            },
            "Farwaniya Hospital": {
                "weekend_days": [],
                "is_rotational_off": True,
                "opening_hours_count": 24,
                "is_24_hour_location": True
            },
            "Bustan": {
                "weekend_days": [],
                "is_rotational_off": True,
                "opening_hours_count": 24,
                "is_24_hour_location": True
            },
            "Jahar Hospital": {
                "weekend_days": [],
                "is_rotational_off": True,
                "opening_hours_count": 24,
                "is_24_hour_location": True
            },
            "Khaitan": {
                "weekend_days": [],
                "is_rotational_off": True,
                "opening_hours_count": 24,
                "is_24_hour_location": True
            },
            "Capital Governorate": {
                "weekend_days": [],
                "is_rotational_off": True,
                "opening_hours_count": 24,
                "is_24_hour_location": True
            },
            # 12-hour locations
            "Admin Science": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            "Life Science": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            "College of Science": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            "Edu Boys": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            "Edu Girls": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            "Edu Girls 2": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            "Marina mall": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
                "weekend_days": [],
            },
            "Boys PAAET": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            "Nursing Girls": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            "Nursing Boys": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            "Makki Juma": {
                "standard_shift_hours": 12,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            "International Hospital": {
                "weekend_days": [],
                "standard_shift_hours": 8,
                "short_t_threshold_hours": 11,
                "more_t_start_hours": 13,
            },
            # Locations with Friday and Saturday weekends, inheriting other defaults
            "Admin Science": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Life Science": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "College of Science": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Edu Boys": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Edu Girls": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Boys PAAET": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "BEAUTY AND TRAVEL": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "PAAET Admin": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Edu Girls 2": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Nursing Girls": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Nursing Boys": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "CIT-SABA SALEM": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Police Force": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "CIT-SABA SALEM": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Edu Boys PAAET": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Admin Tower PAAET": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Capital Governorate": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            "Khaitan": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},

            # "Badriya Hospital": {"weekend_days": [calendar.FRIDAY, calendar.SATURDAY]},
            
        }
    }
}
# --- END COMPANY-SPECIFIC CONFIGURATIONS ---

def normalize_employee_id(emp_id) -> str:
    """
    Robustly normalizes employee IDs to a standard string format.
    Handles:
      - Floats: 1084.0 -> '1084'
      - Integers: 1084 -> '1084'
      - Strings: ' 1084 ' -> '1084', '1084.0' -> '1084'
      - None/NaN: -> ''
    """
    if pd.isna(emp_id):
        return ""
    
    s = str(emp_id).strip()
    
    # Handle '1084.0' specifically
    if '.' in s:
        try:
            # Try to convert to float then to int to remove .0
            f = float(s)
            if f.is_integer():
                return str(int(f))
        except (ValueError, TypeError):
            pass
            
    return s

# --- FILE-SPECIFIC DATE FORMATS ---
# Maps Source_Name (derived from filename) to its specific datetime format string.
# These formats are tried first for matching files.
FILE_DATE_FORMATS = {
    "Benetone Mohalab BM": '%d-%b-%y %I:%M:%S %p',
    "Benetone Mohalab Vm": '%d-%b-%y %I:%M:%S %p',
    "Benetone Mohalab": '%d-%b-%y %I:%M:%S %p',
    "BM D&H Dagher": '%m/%d/%Y %I:%M:%S %p',
    "Celio Marina BM": '%m/%d/%Y %I:%M:%S %p',
    "Celio Marina VM": '%m/%d/%Y %I:%M:%S %p',
    "Celio Marina": '%m/%d/%Y %I:%M:%S %p', # files recveived has 2x space in the middle
    "Celio Warehouse": '%m/%d/%Y %I:%M:%S %p',
    "D&H Dagher Vm": '%m/%d/%Y %I:%M:%S %p',
    "D&H HO": '%m/%d/%Y %I:%M:%S %p',
    "D&H Warehouse": '%m/%d/%Y %I:%M:%S %p',
    "Designer Avenue": '%m/%d/%Y %I:%M:%S %p',
    "Etam 360": '%m/%d/%Y %I:%M:%S %p',
    "Etam 360 Vm": '%d/%m/%Y %I:%M:%S %p',
    "Etam Avenue": '%m/%d/%Y %I:%M:%S %p',
    "Etam Gatemall": '%m/%d/%Y %I:%M:%S %p',
    "Etam Marina": '%m/%d/%Y %I:%M:%S %p',
    "Etam Warehouse": '%m/%d/%Y %I:%M:%S %p',
    "FD Al Bahar BM": '%m/%d/%Y %I:%M:%S %p',
    "FD Al Bahar Vm": '%m/%d/%Y %I:%M:%S %p',
    "FD Boulevard Bm": '%d/%m/%y %I:%M:%S %p',
    "FD Boulevard Vm": '%d/%m/%y %I:%M:%S %p',
    "Head OFfice VM": '%d/%m/%Y %I:%M:%S %p',
    "Lipsy Mohalab": '%d-%b-%y %I:%M:%S %p',
    "Spring Field": '%m/%d/%Y %I:%M:%S %p', # files received with "field" while we use "Field"
    "TT Mohalab": '%d-%b-%y %I:%M:%S %p',
    "Ws Koutmall": '%m/%d/%Y %I:%M:%S %p',
    "Ws 360 Vm": '%d-%b-%y %I:%M:%S %p',
    "Ws 360": '%m/%d/%Y %I:%M:%S %p',
    "Ws Avenue": '%m/%d/%Y %I:%M:%S %p',
    "Ws Gatemall": '%m/%d/%Y %I:%M:%S %p',
    "Ws Mohalab": '%d-%b-%y %I:%M:%S %p',
    "Ws Olympia": '%m/%d/%Y %I:%M:%S %p',
    "Ws Sharq Vm": '%m/%d/%Y %I:%M:%S %p',
    "Ws Sharq": '%m/%d/%Y %I:%M:%S %p',
    "Yammay Avenue": '%m/%d/%Y %I:%M:%S %p',
    "BM FD Boulevard": '%d/%m/%y %I:%M:%S %p',
    "Bm Ws sharq": '%m/%d/%Y %I:%M:%S %p',
    "DCO HO": '%m/%d/%Y %I:%M:%S %p',
    "Yammay Al koutmall": '%m/%d/%Y %I:%M:%S %p',


    # alhadaba
    "Doha Store": '%m/%d/%Y %I:%M:%S %p',

    "Hawally Warehouse ( Hadabah )": '%d/%m/%Y %I:%M:%S %p',
    "Doha Store Warehouse": '%m/%d/%Y %I:%M:%S %p',
    "Hadaba HO": '%m/%d/%Y %I:%M:%S %p',
    "Lighting Plus": '%m/%d/%Y %I:%M:%S %p',
    "S14": '%m/%d/%Y %I:%M:%S %p',
    "S16": '%m/%d/%Y %I:%M:%S %p',
    "S17": '%m/%d/%Y %I:%M:%S %p',
    "S20": '%m/%d/%Y %I:%M:%S %p',
    "S21": '%m/%d/%Y %I:%M:%S %p',
    "S33": '%m/%d/%Y %I:%M:%S %p',
    "S39": '%m/%d/%Y %I:%M:%S %p',
    "S40": '%m/%d/%Y %I:%M:%S %p',
    "S41": '%m/%d/%Y %I:%M:%S %p',
    "S42": '%m/%d/%Y %I:%M:%S %p',
    "Al hadabah Drivers": '%m/%d/%Y %I:%M:%S %p',

    # 2nd cup
    "2nd cup Warehouse": '%m/%d/%Y %I:%M:%S %p',
    "Admin Science": '%m/%d/%Y %I:%M:%S %p',
    "Badriya Hospital": '%m/%d/%Y %I:%M:%S %p',
    "Boys PAAET": '%m/%d/%Y %I:%M:%S %p',
    "Bustan": '%m/%d/%Y %I:%M:%S %p',
    "College of Science": '%m/%d/%Y %I:%M:%S %p',
    "Dar al Shifa Clinic": '%m/%d/%Y %I:%M:%S %p',
    "Dar al Shifa": '%m/%d/%Y %I:%M:%S %p',
    "Edu Boys": '%m/%d/%Y %I:%M:%S %p',
    "Edu Girls 2": '%m/%d/%Y %I:%M:%S %p',
    "Edu Girls": '%m/%d/%Y %I:%M:%S %p',
    "Farwaniya Hospital": '%m/%d/%Y %I:%M:%S %p',
    "Homz Mall": '%m/%d/%Y %I:%M:%S %p',
    "IC Salmiya": '%m/%d/%Y %I:%M:%S %p',
    "International Hospital": '%m/%d/%Y %I:%M:%S %p',
    "Jaber Hospital": '%m/%d/%Y %I:%M:%S %p',
    "Jahar Hospital": '%m/%d/%Y %I:%M:%S %p',
    "Life Science": '%m/%d/%Y %I:%M:%S %p',
    "Makki Juma": '%m/%d/%Y %I:%M:%S %p',
    "Marina Mall": '%m/%d/%Y %I:%M:%S %p',
    "Mohalab": '%m/%d/%Y %I:%M:%S %p',
    "MOI": '%m/%d/%Y %I:%M:%S %p',
    "Nursing Boys": '%m/%d/%Y %I:%M:%S %p',
    "Nursing Girls": '%m/%d/%Y %I:%M:%S %p',
    "PAAET Admin": '%m/%d/%Y %I:%M:%S %p',
    "Scup Vm": '%m/%d/%Y %I:%M:%S %p',
    "BEAUTY AND TRAVEL": '%m/%d/%Y %I:%M:%S %p',
    "CIT": '%m/%d/%Y %I:%M:%S %p',
    "Edu Boys PAAET": '%m/%d/%Y %I:%M:%S %p',
    "Khaitan": '%m/%d/%Y %I:%M:%S %p',
    "Capital Governorate": '%m/%d/%Y %I:%M:%S %p',
    "Police Force": '%m/%d/%Y %I:%M:%S %p',
    "Adan Hospital": '%m/%d/%Y %I:%M:%S %p',
    "Scup jaber Dental": '%m/%d/%Y %I:%M:%S %p',

    # D&Co
    "BEBE Olympia": '%m/%d/%Y %I:%M:%S %p',
    "BYL Mohalab": '%d-%b-%y %I:%M:%S %p',
    "BYL 360": '%m/%d/%Y %I:%M:%S %p',
    "BYL Avenue": '%m/%d/%Y %I:%M:%S %p',
    "BYL Koutmall": '%m/%d/%Y %I:%M:%S %p',
    "FD Al Bahar": '%m/%d/%Y %I:%M:%S %p',
    "FD Boulevard": '%d/%m/%y %I:%M:%S %p',
    "FD Olympia": '%m/%d/%Y %I:%M:%S %p',
    "Hunkemoller": '%m/%d/%Y %I:%M:%S %p',
    "LVER 360": '%m/%d/%Y %I:%M:%S %p',
    "LVER Avenue": '%m/%d/%Y %I:%M:%S %p',
    "LVER Koutmall": '%m/%d/%Y %I:%M:%S %p',
    "LVER Gatemall": '%m/%d/%Y %I:%M:%S %p',
    "LVER Olympia": '%m/%d/%Y %I:%M:%S %p',
    "LVER Al Raya": '%m/%d/%Y %I:%M:%S %p',
    "LVER Mohalab": '%d-%b-%y %I:%M:%S %p',
    "Menbur Avenue": '%m/%d/%Y %I:%M:%S %p',
    "DCO HO": '%m/%d/%Y %I:%M:%S %p',
    "Hunkemoller Avenue": '%m/%d/%Y %I:%M:%S %p',
}
# --- END FILE-SPECIFIC DATE FORMATS ---

# =====================================================================
# NUMERIC FILE NAME → LOCATION MAPPING
# =====================================================================

LOCATION_MAP = {
    # D&H = 1
    "D&H": {
        "Benetone Mohalab BM": "01",
        "Benetone Mohalab Vm": "02",
        "Benetone Mohalab": "03",
        "BM D&H Dagher": "04",
        "Celio Marina BM": "05",
        "Celio Marina VM": "06",
        "Celio Marina": "07",
        "Celio Warehouse": "08",
        "D&H Dagher Vm": "09",
        "D&H HO": "10",
        "D&H Warehouse": "11",
        "Designer Avenue": "12",
        "Etam 360": "13",
        "Etam 360 Vm": "14",
        "Etam Avenue": "15",
        "Etam Gatemall": "16",
        "Etam Marina": "17",
        "Etam Warehouse": "18",
        "FD Al Bahar BM": "19",
        "FD Al Bahar Vm": "20",
        "FD Boulevard Bm": "21",
        "FD Boulevard Vm": "22",
        "Head OFfice VM": "23",
        "Lipsy Mohalab": "24",
        "Spring Field": "25",
        "TT Mohalab": "26",
        "Ws Koutmall": "27",
        "Ws 360 Vm": "28",
        "Ws 360": "29",
        "Ws Avenue": "30",
        "Ws Gatemall": "31",
        "Ws Mohalab": "32",
        "Ws Olympia": "33",
        "Ws Sharq Vm": "34",
        "Ws Sharq": "35",
        "Yammay Avenue": "36",
        "BM FD Boulevard": "37",
        "Bm Ws sharq": "38",
        "DCO HO": "39",
        "Yammay Al koutmall": "40",
    },
    # Al-hadabah times = 4
    "Al-hadabah times": {
        "Doha Store": "01",
        "Hawally Warehouse ( Hadabah )": "02",
        "Doha Store Warehouse": "03",
        "Hadaba HO": "04",
        "Lighting Plus": "05",
        "S14": "06",
        "S16": "07",
        "S17": "08",
        "S20": "09",
        "S21": "10",
        "S33": "11",
        "S39": "12",
        "S40": "13",
        "S41": "14",
        "S42": "15",
        "Al hadabah Drivers": "16",
    },
    # Second Cup = 3
    "Second Cup": {
        "2nd cup Warehouse": "01",
        "Admin Science": "02",
        "Badriya Hospital": "03",
        "Boys PAAET": "04",
        "Bustan": "05",
        "College of Science": "06",
        "Dar al Shifa Clinic": "07",
        "Dar al Shifa": "08",
        "Edu Boys": "09",
        "Edu Girls 2": "10",
        "Edu Girls": "11",
        "Farwaniya Hospital": "12",
        "Homz Mall": "13",
        "IC Salmiya": "14",
        "International Hospital": "15",
        "Jaber Hospital": "16",
        "Jahar Hospital": "17",
        "Life Science": "18",
        "Makki Juma": "19",
        "Marina Mall": "20",
        "Mohalab": "21",
        "MOI": "22",
        "Nursing Boys": "23",
        "Nursing Girls": "24",
        "PAAET Admin": "25",
        "Scup Vm": "26",
        "BEAUTY AND TRAVEL": "27",
        "CIT": "28",
        "Edu Boys PAAET": "29",
        "Khaitan": "30",
        "Capital Governorate": "31",
        "Police Force": "32",
        "Adan Hospital": "33",
        "DASHCO": "34",
        "Scup jaber Dental": "35",
    },
    # D&co = 2
    "D&co": {
        "BEBE Olympia": "01",
        "BYL Mohalab": "02",
        "BYL 360": "03",
        "BYL Avenue": "04",
        "BYL Koutmall": "05",
        "FD Al Bahar": "06",
        "FD Boulevard": "07",
        "FD Olympia": "08",
        "Hunkemoller": "09",
        "LVER 360": "10",
        "LVER Avenue": "11",
        "LVER Koutmall": "12",
        "LVER Gatemall": "13",
        "LVER Olympia": "14",
        "LVER Al Raya": "15",
        "LVER Mohalab": "16",
        "Menbur Avenue": "17",
        "DCO HO": "18",
        "Hunkemoller Avenue": "19",
    },
    # D&CO Jordan = 5 (locations are added via the Store Management page)
    "D&CO Jordan": {},
}

# =====================================================================
# STORE OPERATIONS CRITERIA LINKS (Google Sheets)
# =====================================================================
# Maps Source_Name → Google Sheet Export URL
# kuwait links 
STORE_OPS_LINKS = {
    "Etam Avenue": "https://docs.google.com/spreadsheets/d/153tgWpTT65qOVL_KJpGOMP7xNYmG-Sc5JNNIhcsz490/export?format=csv",
    "Yammay Avenue": "https://docs.google.com/spreadsheets/d/1O3b842Nvwgb-HIpBZ--cEMfcnlRrKmfJ8HNa0TccF14/export?format=csv",
    "Ws Gatemall": "https://docs.google.com/spreadsheets/d/15wFd-tdzSr4AtJ9bgmelju0XoAVcCL4EPDeMfqdWkbg/export?format=csv",
    "Etam Gatemall": "https://docs.google.com/spreadsheets/d/1nKtjIlcPkOH6jPcWAfEDSq9uxA4iap80Bjpch-LHg8Y/export?format=csv",
    "Ws Mohalab": "https://docs.google.com/spreadsheets/d/1U0bIjdb6MEzlN_i83s86TG6k4Xd64hRlcbm3P7wcs_o/export?format=csv",
    "TT Mohalab": "https://docs.google.com/spreadsheets/d/1EgrYSYxvcEg0DIuilrQLdutzW-jmKhqyoElZNQshUf8/export?format=csv",
    "Benetone Mohalab": "https://docs.google.com/spreadsheets/d/1o9tibo9_zlmbwBB4VKAiJK6sabGkhCK_hOyeHWl2xi8/export?format=csv",
    "Ws Sharq": "https://docs.google.com/spreadsheets/d/1gNTn5xfVIH8mY8-BWabPAAemoQGzO27Yf3__5OgNXhY/export?format=csv",
    "Ws Koutmall": "https://docs.google.com/spreadsheets/d/167dhfW8-4M7Z-T9gtat6MgNuIT1iOiNdSO8WGKktNDY/export?format=csv",
    "Yammay Al koutmall": "https://docs.google.com/spreadsheets/d/1rxxfgnrlQMr9OaKOIOwYlL-ZN5FXbXat1i3F_9w9HQQ/export?format=csv",
    "Etam Marina": "https://docs.google.com/spreadsheets/d/1tk1fWxxNGmWKpK3kSqI01JFGd7AlUNZeImZcjOMXJpc/export?format=csv",
    "Celio Marina": "https://docs.google.com/spreadsheets/d/1hahRBpfD02oLKcxsvdDSZVEhkMT4YeAz1dg3dj6e24c/export?format=csv",
    "Etam Warehouse": "https://docs.google.com/spreadsheets/d/1xScMArE5q7w7iU8phhY_y1l_B9SIO1oEC0MUmtyBTRg/export?format=csv",
    "Celio Warehouse": "https://docs.google.com/spreadsheets/d/1Tz96_oel75cno1kdRUmhRqBhGkcBsMit-kxxOLEg5_Q/export?format=csv",
    "Spring Field": "https://docs.google.com/spreadsheets/d/1aKR_nleV4eO9TJNHv0a8BXKutCBY_CeuJLIATXcoyB4/export?format=csv",
    "Designer Avenue": "https://docs.google.com/spreadsheets/d/1QvEUOisRktU33zhWcCxhq39F2MlN72GM-D6wjZPrhyI/export?format=csv",
    "D&H Warehouse": "https://docs.google.com/spreadsheets/d/1nA5qlW2MA9gp39OLZqO4Y9B4oAbvifJHuFIOYjk7eCI/export?format=csv",
    "S21": "https://docs.google.com/spreadsheets/d/1O8y7iuTZ-6jzsz_UJgflHsnolspSCIlTccHnQ3SiuJw/export?format=csv",
    "Doha Store Warehouse": "https://docs.google.com/spreadsheets/d/1VeApY8r7bVXcgOu6-J5toKbASNSRtHQdJWozNsYu0hI/export?format=csv",
    "Doha Store": "https://docs.google.com/spreadsheets/d/1dWE2NyI2bRS-k2uzDNBH7zYVYI4yOsDnCr7HaGtkqqI/export?format=csv",
    "S17": "https://docs.google.com/spreadsheets/d/1Lua5oVoPAeO9rccEmmX8L8a6b418xDe-6r_AyBf_dPg/export?format=csv",
    "S41": "https://docs.google.com/spreadsheets/d/1JbhsFZWPZgxXVe4-PlqeqUZFy5k8bufHE1SD_STStTI/export?format=csv",
    "S33": "https://docs.google.com/spreadsheets/d/1s0vTurRXOK8lwrnoXNDnpF8G1BDm4svvxSr7osGQbWk/export?format=csv",
    "Hadaba HO": "https://docs.google.com/spreadsheets/d/1jtCTBHnHmdQX8cMTYOL7Dj-kuX0nkKzGNgp0SmnTOnA/export?format=csv",
    "Hunkemoller Avenue": "https://docs.google.com/spreadsheets/d/1YZiP-0bltMIOnGEq1oSuMulcpVzM5PL_NM13dFhuqK8/export?format=csv",
    "S40": "https://docs.google.com/spreadsheets/d/1QtWsNwKm6ChnoLhw368jrpXX6B-xbWSZnscQ0E6ea0c/export?format=csv",
    "Hawally Warehouse ( Hadabah )": "https://docs.google.com/spreadsheets/d/1easCQaB098EO1_rw0sKuNf6SXDLvSbE4D0RoiCUH-y4/export?format=csv",
    "Al hadabah Drivers": "https://docs.google.com/spreadsheets/d/1OH0ko6btNzsqBXKP65sDzOXwbjM-DMLcdK9_1Sjphpo/export?format=csv",
    "Lighting Plus": "https://docs.google.com/spreadsheets/d/1XuqWn1ExRllisPEMVD-l0noo1_5yjADi6qxP02tmSLA/export?format=csv",
    "S39": "https://docs.google.com/spreadsheets/d/1Fp5aOxXDLlNHr2Mxw5CCdqyE231CJHha1qg92ca9Q6U/export?format=csv",
    "S16": "https://docs.google.com/spreadsheets/d/1_rYcZoqKXw8VAyX91CJFHe7oOC1OM2PfBrW9qucg7z4/export?format=csv",
    "S14": "https://docs.google.com/spreadsheets/d/16oQHWV6zYhJlEISQcibTFbU4RtJGug6lwjHJpsnfiuc/export?format=csv",
    "S20": "https://docs.google.com/spreadsheets/d/1JtsMMCU79bFQhEwq4cUFDOsVSv9obJRS1dSDeIucqDQ/export?format=csv",
    "S42": "https://docs.google.com/spreadsheets/d/1gwm11GBN7KhBh4xf93-0JQfY42bfKXd0wH7kGCznKwk/export?format=csv",
    "brand managers": "https://docs.google.com/spreadsheets/d/1zIzNvg62fu3aiSorYuQHyd6QeY_HeyPKWrTYxeUCqhk/export?format=csv",
    "floor managers": "https://docs.google.com/spreadsheets/d/1zR79LssZ8FkZtkYUTPmacVookCtmZCYb5VPhZHnruTE/export?format=csv",
    "Warehouse": "https://docs.google.com/spreadsheets/d/1opWFJv14RyvOAafIzJu9d1b60AkGOkCQvcFlAT9chkc/export?format=csv",
    "Marina Mall": "https://docs.google.com/spreadsheets/d/1CKG2tYMLC6qDY4Z1I43rR63FaFydTJBQNRyaB26NeEw/export?format=csv",
    "Bustan": "https://docs.google.com/spreadsheets/d/192g5jq4CbRo30kmgUUimk8_yAPOywkTWXgG4s6zI5nk/export?format=csv",
    "DASHCO": "https://docs.google.com/spreadsheets/d/1D8mffrtNGvY_wnt8jJCpUmJClN-xmqlSGdeu2e-iwqY/export?format=csv",
    "Admin Science": "https://docs.google.com/spreadsheets/d/1RYDX-jPNeB52VAC5ovv6hXBWlXe1etihLvx544aT3l4/export?format=csv",
    "Life Science": "https://docs.google.com/spreadsheets/d/1-H2NJDF1L-6DRXJNbOPTh-x9Xi9FCE0_OBrC6YkO4zQ/export?format=csv",
    "International Hospital": "https://docs.google.com/spreadsheets/d/14IUbRRpsnO6s_rWgOqA3GgRYR71x6b9m_iYtO-pNGKo/export?format=csv",
    "Mohalab": "https://docs.google.com/spreadsheets/d/19dtrtH6kCLp_etG6dva03anTIiLYtHlqivdF37MoV44/export?format=csv",
    "College of Science": "https://docs.google.com/spreadsheets/d/1JWALXVWWm5e0B9GA-dW_PMNHVK5Y94FIxjVwiNNLo8c/export?format=csv",
    "Makki Juma": "https://docs.google.com/spreadsheets/d/1v47A4y1Ys6I_F1927ymABuqxQaI0tV3-V1-B_F92xk4/export?format=csv",
    "Police Force": "https://docs.google.com/spreadsheets/d/1fXSAmk0MZwIIbZf2-xbgs5804eFcIOGFanNdny5sIy4/export?format=csv",
    "Jahar Hospital": "https://docs.google.com/spreadsheets/d/1ud8koWY2v7_c5T4y--6Slrtn8UxE2GN_VvSt23DmOsU/export?format=csv",
    "Farwaniya Hospital": "https://docs.google.com/spreadsheets/d/1-NyjZgwaWv1bvpF5PUz_1Izw2dRgZ48v7BgGfe1f6xQ/export?format=csv",
    "Jaber Hospital": "https://docs.google.com/spreadsheets/d/1iy6pgd7CiXZR8Lau7dvd7gtpVHq-chq1TDi7MBaWnsQ/export?format=csv",
    "Badriya Hospital": "https://docs.google.com/spreadsheets/d/1wurL9jUXypUObHwgjRotBd22-QdwJ3wEAPfJ0hKytNg/export?format=csv",
    "BEAUTY AND TRAVEL": "https://docs.google.com/spreadsheets/d/1VWbNLzKgcfxUQx1YLttiAyf3_s5ITzVfuOVcD_vaOio/export?format=csv",
    "CIT": "https://docs.google.com/spreadsheets/d/1F4sSTHjLn4F-UHGVXBWc-x9mxcllYs1r8j2LG_tiu8g/export?format=csv",
    "Nursing Boys": "https://docs.google.com/spreadsheets/d/1xVGaeF6QO-EaE3tnaFkgQzGN1SXYNIWO8W8xWIImjp4/export?format=csv",
    "Nursing Girls": "https://docs.google.com/spreadsheets/d/1MRWfpWMOhmyAP7k8oT9m5Tw6ikYhW_fNEVgula-3GOs/export?format=csv",
    "Edu Boys": "https://docs.google.com/spreadsheets/d/19HGjc334GKdgFr3ACMEyNvlUjgJgP0mOiMO_-YyskZc/export?format=csv",
    "Edu Boys PAAET": "https://docs.google.com/spreadsheets/d/1ydEouRS6QJmbhmmnC_tZUWhEdy5ghuxOsVTN8DKNZxs/export?format=csv",
    "Edu Girls": "https://docs.google.com/spreadsheets/d/1kQzTAw_TopvmP5QL7E9initiF_xTXdPkC9LnKME5nyI/export?format=csv",
    "Edu Girls 2": "https://docs.google.com/spreadsheets/d/1ruvMegtyC9QmOz4hK4RulS0HqJmcNpBZ5UKev4VBVvw/export?format=csv",
    "PAAET Admin": "https://docs.google.com/spreadsheets/d/19nFvunZ4GLbb9VZ_bmj_lvI_5N4wxC6lSr5TO3nx5pM/export?format=csv",
    "Khaitan": "https://docs.google.com/spreadsheets/d/1JsqzNF_M3aj_Tg7G6P_AkWjWrPUjTHjqoOdnCz62Wdc/export?format=csv",
    "Capital Governorate": "https://docs.google.com/spreadsheets/d/1L1KoxiAMxvn13zpW6hvISFhWdFqo_WkFnets58yRiyE/export?format=csv",
    "Adan Hospital": "https://docs.google.com/spreadsheets/d/1XNj1Tdr2k-JBFpj0Qod-AjEVpyVuj-t8jItVAyHl9Cw/export?format=csv",
    "Scup jaber Dental": "https://docs.google.com/spreadsheets/d/1Sjlx0i7nIExBNiuewu5CFG35sLj5tfZ0SO3gsTcCEh0/export?format=csv",
    "2nd cup Warehouse": "https://docs.google.com/spreadsheets/d/1uRNl-KdUHtWx2NGVnI0tUcKx_qshwag-llvW5NKougE/export?format=csv",
    "Ws Olympia": "https://docs.google.com/spreadsheets/d/1i1T6ED5n_JnMzwWzl4XqP1He3XtGe4ubei0IPv7IRtg/export?format=csv",
    "Ws 360": "https://docs.google.com/spreadsheets/d/1jF2SHpPS0lEvG-nxz7TLRfrU-X2yqhTbwvBiL2NYL_c/export?format=csv",
    "Etam 360": "https://docs.google.com/spreadsheets/d/1o8QTsay4QYeQ_CPlh3xvkY99He1G8aF4VlnQRZEBIYw/export?format=csv",
    "Ws Avenue": "https://docs.google.com/spreadsheets/d/1xlIeoD_CU5l6-wHr8Nuc5ASoUlxmtg2Tfj32Yvcc00Y/export?format=csv",
    "LVER 360": "https://docs.google.com/spreadsheets/d/1O8y7iuTZ-6jzsz_UJgflHsnolspSCIlTccHnQ3SiuJw/export?format=csv",
    "BYL 360": "https://docs.google.com/spreadsheets/d/1VeApY8r7bVXcgOu6-J5toKbASNSRtHQdJWozNsYu0hI/export?format=csv",
    "BEBE Olympia": "https://docs.google.com/spreadsheets/d/1dWE2NyI2bRS-k2uzDNBH7zYVYI4yOsDnCr7HaGtkqqI/export?format=csv",
    "FD Olympia": "https://docs.google.com/spreadsheets/d/1Lua5oVoPAeO9rccEmmX8L8a6b418xDe-6r_AyBf_dPg/export?format=csv",
    "LVER Olympia": "https://docs.google.com/spreadsheets/d/1JbhsFZWPZgxXVe4-PlqeqUZFy5k8bufHE1SD_STStTI/export?format=csv",
    "LVER Avenue": "https://docs.google.com/spreadsheets/d/1s0vTurRXOK8lwrnoXNDnpF8G1BDm4svvxSr7osGQbWk/export?format=csv",
    "BYL Avenue": "https://docs.google.com/spreadsheets/d/1jtCTBHnHmdQX8cMTYOL7Dj-kuX0nkKzGNgp0SmnTOnA/export?format=csv",
    "LVER Gatemall": "https://docs.google.com/spreadsheets/d/1QtWsNwKm6ChnoLhw368jrpXX6B-xbWSZnscQ0E6ea0c/export?format=csv",
    "BYL Mohalab": "https://docs.google.com/spreadsheets/d/1easCQaB098EO1_rw0sKuNf6SXDLvSbE4D0RoiCUH-y4/export?format=csv",
    "LVER Mohalab": "https://docs.google.com/spreadsheets/d/1OH0ko6btNzsqBXKP65sDzOXwbjM-DMLcdK9_1Sjphpo/export?format=csv",
    "BYL Koutmall": "https://docs.google.com/spreadsheets/d/1XuqWn1ExRllisPEMVD-l0noo1_5yjADi6qxP02tmSLA/export?format=csv",
    "LVER Koutmall": "https://docs.google.com/spreadsheets/d/1Fp5aOxXDLlNHr2Mxw5CCdqyE231CJHha1qg92ca9Q6U/export?format=csv",
    "FD Boulevard": "https://docs.google.com/spreadsheets/d/1_rYcZoqKXw8VAyX91CJFHe7oOC1OM2PfBrW9qucg7z4/export?format=csv",
    "FD Al Bahar": "https://docs.google.com/spreadsheets/d/16oQHWV6zYhJlEISQcibTFbU4RtJGug6lwjHJpsnfiuc/export?format=csv",
    "Hunkemoller": "https://docs.google.com/spreadsheets/d/1JtsMMCU79bFQhEwq4cUFDOsVSv9obJRS1dSDeIucqDQ/export?format=csv",
    "LVER Al Raya": "https://docs.google.com/spreadsheets/d/1gwm11GBN7KhBh4xf93-0JQfY42bfKXd0wH7kGCznKwk/export?format=csv",
}



def resolve_location_from_numeric(filename: str):
    """
    Convert numeric filename like '111.xlsx' → real location name.
    Format: CLLL
        C   = company number (1,2,3,4)
        LLL = location number (no leading zeros)
    Returns the location name or None.
    """
    import os

    base = os.path.splitext(filename)[0].strip()

    # Must be numeric
    if not base.isdigit():
        return None

    # Company = first digit
    company = base[0]

    # Location code = rest
    location = base[1:]
    if not location:
        return None

    company_dict = LOCATION_MAP.get(company)
    if not company_dict:
        return None

    return company_dict.get(location)


# --- Column Name Mapping ---
# Maps standard internal column names to potential external column names found in uploaded files.
# The order of the list matters: it will try to find columns in this order.
COLUMN_MAPPING = {
    'No.': ['No.', 'AC-No.'],
    'Name': ['Name'],
    'Date/Time': ['Date/Time', 'Time'], # 'Time' is already here
    'Status': ['Status', 'State']
}
# --- END Column Mapping ---

# --- Helper Function: Formats a pandas Timedelta object into HH:MM:SS string. ---
def format_timedelta_to_hms(td):
    """
    Formats a pandas Timedelta object into HH:MM:SS string.
    Returns '00:00:00' for NaN values.
    """
    if pd.isna(td):
        return '00:00:00'
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Function to safely merge dictionaries, with later dicts overriding earlier ones
def merge_configs(base, override):
    """
    Recursively merges two dictionaries. Values from 'override' overwrite 'base' values.
    If a key exists in both and its value is a dictionary, the dictionaries are merged.
    """
    merged = base.copy()
    if override:
        for k, v in override.items():
            if isinstance(merged.get(k), dict) and isinstance(v, dict):
                merged[k] = merge_configs(merged[k], v)
            else:
                merged[k] = v
    return merged

def get_effective_rules_for_employee_day(company_name: str, employee_no: str, source_name: str) -> dict:
    """
    Determines the effective rules for a given employee on a specific day,
    applying hierarchy: Default -> Location -> Employee Override.
    Also handles implicit rotational status if a location has no fixed weekend days.
    """
    company_config = COMPANY_CONFIGS.get(company_name, {})
    
    # Start with default rules for the company
    effective_rules = company_config.get("default_rules", {}).copy()

    # Apply location-specific overrides
    location_rules = company_config.get("location_rules", {}).get(source_name, {})
    effective_rules = merge_configs(effective_rules, location_rules)

    # --- Reverted Logic: Only imply rotational if explicitly empty/None ---
    if (effective_rules.get("weekend_days") == [] or effective_rules.get("weekend_days") is None) and \
       not effective_rules.get("is_rotational_off", False):
        effective_rules["is_rotational_off"] = True
        if "rotational_days_off_per_week" not in effective_rules:
            effective_rules["rotational_days_off_per_week"] = 1
    # --- End New Logic ---

    # Apply employee-specific overrides (highest precedence)
    employee_rules = company_config.get("employee_overrides", {}).get(employee_no, {})
    effective_rules = merge_configs(effective_rules, employee_rules)
    
    return effective_rules

# Helper to get expected working days for a period, considering alternating weekends
def get_expected_working_days_in_period(start_date, end_date, rules: dict) -> float: # Return float for precision
    """
    Calculates the number of expected working days within a given date range,
    considering company-specific weekend rules, including alternating weekends and rotational offs.
    Returns the expected number of working days (can be float for rotational).
    """
    if start_date is None or end_date is None or start_date > end_date:
        return 0.0

    total_days_in_period_float = (end_date - start_date).days + 1.0 # Use float for calculations

    is_rotational_off = rules.get("is_rotational_off", False)
    rotational_days_off_per_week = rules.get("rotational_days_off_per_week", 1) # Default 1 day off for rotational

    if is_rotational_off:
        # Calculate expected off days based on rate per week
        expected_off_days_exact = total_days_in_period_float * (rotational_days_off_per_week / 7.0)
        expected_working_days_exact = total_days_in_period_float - expected_off_days_exact
        return expected_working_days_exact
    else:
        expected_days = 0
        current_date = start_date
        
        weekend_days = rules.get("weekend_days", [calendar.FRIDAY, calendar.SATURDAY])
        weekend_rule_type = rules.get("weekend_rule_type", "fixed") # "fixed" or "alternating_f_fs"

        while current_date <= end_date:
            day_of_week = current_date.weekday() # Monday is 0, Sunday is 6

            is_weekend = False
            if weekend_rule_type == "fixed":
                if day_of_week in weekend_days:
                    is_weekend = True
                else:
                    is_weekend = False
            elif weekend_rule_type == "alternating_f_fs":
                iso_week_number = current_date.isocalendar()[1]
                if (iso_week_number % 2) == 1: # Odd weeks: Friday only (Week 1, 3, 5...)
                    if day_of_week == calendar.FRIDAY:
                        is_weekend = True
                    else:
                        is_weekend = False
                else: # Even weeks: Friday and Saturday (Week 2, 4, 6...)
                    if day_of_week == calendar.FRIDAY or day_of_week == calendar.SATURDAY:
                        is_weekend = True
                    else:
                        is_weekend = False
            
            if not is_weekend:
                expected_days += 1
            
            current_date += timedelta(days=1)
        return float(expected_days) # Return float even for fixed, for consistency


# ----------------------------------------------------------------------
# CUSTOM STORES OVERLAY (managed by the Store Management page)
# ----------------------------------------------------------------------
# Stores added through the app live in custom_stores.json (committed to
# GitHub by the Store Management page). They are merged into the config
# structures above at import time, so the rest of the app sees them as if
# they were defined here. This section only ADDS configuration; it does
# not change any calculation logic.
import json as _json
import os as _os
import copy as _copy

# Snapshot of the stores defined in this file, taken before the overlay is
# merged, so the Store Management page can tell built-in stores from added ones.
BUILTIN_LOCATION_MAP = _copy.deepcopy(LOCATION_MAP)

# Date formats and Google Sheet links are keyed by store name across ALL
# companies, so a new store must not reuse any name already configured here.
BUILTIN_STORE_NAMES = (
    {name for stores in LOCATION_MAP.values() for name in stores}
    | set(FILE_DATE_FORMATS)
    | set(STORE_OPS_LINKS)
)

CUSTOM_STORES_FILE =_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "custom_stores.json")


def load_custom_stores() -> dict:
    """Returns the custom stores overlay: { company: { store_name: {...} } }."""
    try:
        with open(CUSTOM_STORES_FILE, encoding="utf-8") as f:
            data = _json.load(f)
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}
    except Exception:
        # A broken JSON must never stop the app; the overlay is simply skipped.
        return {}


def _apply_custom_stores():
    for company, stores in load_custom_stores().items():
        if not isinstance(stores, dict):
            continue
        for name, s in stores.items():
            if not isinstance(s, dict):
                continue
            # 1) File-number mapping (numeric filenames -> store name)
            if s.get("code"):
                LOCATION_MAP.setdefault(company, {})[name] = str(s["code"])
            # 2) Date format of the fingerprint export
            if s.get("date_format"):
                FILE_DATE_FORMATS[name] = s["date_format"]
            # 3) Google Sheet schedule link for Store Ops checks
            if s.get("store_ops_link"):
                STORE_OPS_LINKS[name] = s["store_ops_link"]
            # 4) Location rules (weekends + working hours)
            rules = {"weekend_days": s.get("weekend_days", []), "is_rotational_off": False}
            wh = s.get("working_hours")
            if wh in (8, 9):
                rules["standard_shift_hours"] = wh
                rules["short_t_threshold_hours"] = wh - 0.5
                rules["more_t_start_hours"] = wh + 1
            elif wh in (12, 24):
                rules["opening_hours_count"] = wh
                if wh == 24:
                    rules["is_24_hour_location"] = True
            if not s.get("weekend_days"):
                # No fixed weekend -> rotational offs (matches existing app logic)
                rules["is_rotational_off"] = True
                rules["rotational_days_off_per_week"] = 1
            company_cfg = COMPANY_CONFIGS.setdefault(company, {"default_rules": {}, "location_rules": {}})
            existing_rules = company_cfg.setdefault("location_rules", {}).get(name, {})
            company_cfg["location_rules"][name] = merge_configs(existing_rules, rules)


_apply_custom_stores()
