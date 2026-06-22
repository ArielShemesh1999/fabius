"""
Centralized configuration for the NexShift Agent.

All configurable parameters that are shared across modules should be defined here.
"""

import os

# =============================================================================
# LLM Model Names
# =============================================================================
# Models used by each agent. Override via environment variables if needed.

MODEL_COORDINATOR = os.environ.get(
    "NEXSHIFT_MODEL_COORDINATOR", "gemini-3.0-flash"
)
MODEL_CONTEXT_GATHERER = os.environ.get(
    "NEXSHIFT_MODEL_CONTEXT_GATHERER", "gemini-3.0-flash"
)
MODEL_SOLVER = os.environ.get("NEXSHIFT_MODEL_SOLVER", "gemini-3.0-flash")
MODEL_COMPLIANCE = os.environ.get("NEXSHIFT_MODEL_COMPLIANCE", "gemini-3.1-pro")
MODEL_EMPATHY = os.environ.get("NEXSHIFT_MODEL_EMPATHY", "gemini-3.1-pro")
MODEL_PRESENTER = os.environ.get("NEXSHIFT_MODEL_PRESENTER", "gemini-3.0-flash")

# =============================================================================
# Shift Time Boundaries (24-hour clock)
# =============================================================================
# Hour thresholds for classifying shift types
NIGHT_SHIFT_START_HOUR = 20  # 20:00+ = night shift
DAY_SHIFT_START_HOUR = 6  # 06:00-13:59 = day shift
EVENING_SHIFT_START_HOUR = 14  # 14:00-19:59 = evening shift
LATE_SHIFT_CONFLICT_HOUR = (
    16  # 16:00+ treated as evening/night for rest-gap analysis
)

# =============================================================================
# Weekend Detection
# =============================================================================
# Python weekday(): Mon=0..Sun=6; Saturday=5
WEEKEND_WEEKDAY_START = 5

# =============================================================================
# Fatigue Thresholds
# =============================================================================
# Display/reporting thresholds (empathy, query, history tools)
FATIGUE_DISPLAY_HIGH = 0.7
FATIGUE_DISPLAY_MODERATE = 0.4

# Solver optimization thresholds (stricter, solver_tool.py only)
FATIGUE_SOLVER_HIGH = 0.8
FATIGUE_SOLVER_MODERATE = 0.5

# Capacity reduction factors when fatigued (solver)
FATIGUE_HIGH_CAPACITY_FACTOR = 0.5  # 50% capacity
FATIGUE_MODERATE_CAPACITY_FACTOR = 0.75  # 75% capacity

# =============================================================================
# Scheduling Constraints
# =============================================================================
MAX_CONSECUTIVE_SHIFTS = 3
MIN_REST_HOURS = 8
MIN_SENIOR_NURSES = 2  # Minimum senior nurses for adequate coverage

# =============================================================================
# Burnout Alert Thresholds
# =============================================================================
# Shift counts that trigger burnout warnings in empathy analysis
BURNOUT_HEAVY_WORKLOAD_SHIFTS = 5
BURNOUT_MANY_NIGHT_SHIFTS = 3
BURNOUT_MULTIPLE_WEEKEND_SHIFTS = 2

# =============================================================================
# Shift Fairness
# =============================================================================
# Variance thresholds for shift distribution across nurses
SHIFT_VARIANCE_HIGH = 3
SHIFT_VARIANCE_MODERATE = 2

# Empathy score deductions for shift imbalance
SHIFT_VARIANCE_HIGH_DEDUCTION = 0.2
SHIFT_VARIANCE_MODERATE_DEDUCTION = 0.1

# =============================================================================
# Empathy Scoring
# =============================================================================
EMPATHY_GOOD_THRESHOLD = 0.8
EMPATHY_ACCEPTABLE_THRESHOLD = 0.6

# Empathy penalty multipliers
EMPATHY_PREFERENCE_PENALTY = 0.02
EMPATHY_PREFERENCE_PENALTY_CAP = 0.3
EMPATHY_BURNOUT_PENALTY = 0.05
EMPATHY_BURNOUT_PENALTY_CAP = 0.3

# =============================================================================
# Fatigue Score Calculation (history_tools.py)
# =============================================================================
# Divisors for normalizing raw counts into 0-1 range
FATIGUE_CONSECUTIVE_DIVISOR = 3
FATIGUE_WEEKLY_HOURS_DIVISOR = 4
FATIGUE_REST_HOURS_DIVISOR = 8

# Component weights (must sum to 1.0)
FATIGUE_WEIGHT_CONSECUTIVE = 0.3
FATIGUE_WEIGHT_WEEKLY_HOURS = 0.25
FATIGUE_WEIGHT_REST_GAP = 0.25
FATIGUE_WEIGHT_PATTERN = 0.2

# =============================================================================
# Display / Formatting Limits
# =============================================================================
DISPLAY_MAX_ITEMS = 10
DISPLAY_OVERLAP_DATES = 5  # Max overlap dates shown before truncating
MAX_INLINE_DATES = 7  # Max time-off dates shown inline before truncating

# =============================================================================
# Seniority & Contract Mappings
# =============================================================================
SENIORITY_ORDER = {"Junior": 1, "Mid": 2, "Senior": 3}
MAX_HOURS_BY_CONTRACT = {"FullTime": 40, "PartTime": 30, "Casual": 20}

# =============================================================================
# Solver Tuning (OR-Tools CP-SAT parameters)
# =============================================================================
SOLVER_MAX_TIME_SECONDS = 30.0
SOLVER_NUM_WORKERS = 8
SOLVER_UTILIZATION_THRESHOLD = 0.75  # Warn above 75% daily utilization
SOLVER_CAPACITY_THRESHOLD = 0.9  # Warn above 90% ward capacity

# Objective function weights (positive = bonus, negative = penalty)
WEIGHT_SENIOR_BONUS = 3
WEIGHT_PREFERRED_DAY_BONUS = 5
WEIGHT_FATIGUE_HIGH_PENALTY = -50
WEIGHT_FATIGUE_MODERATE_PENALTY = -25
WEIGHT_FATIGUE_WEEKEND_PENALTY = -30
WEIGHT_FATIGUE_NIGHT_PENALTY = -30
WEIGHT_AVOID_NIGHT_PENALTY = -50
WEIGHT_EXCESS_SHIFTS_PENALTY = -10
WEIGHT_DEFICIT_SHIFTS_PENALTY = -15
WEIGHT_WEEKEND_EXCESS_PENALTY = -30
WEIGHT_NIGHT_EXCESS_PENALTY = -30
