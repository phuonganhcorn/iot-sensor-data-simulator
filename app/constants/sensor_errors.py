# Constants for sensor errors
NO_ERROR = "no_error"
ANOMALY = "anomaly"
MCAR = "mcar"
DUPLICATE_DATA = "duplicate_data"
DRIFT = "drift"
PROBABILITY_POS_ANOMALY = "probability_pos_anomaly"
PROBABILITY_NEG_ANOMALY = "probability_neg_anomaly"
POS_ANOMALY_UPPER_RANGE = "pos_anomaly_upper_range"
POS_ANOMALY_LOWER_RANGE = "pos_anomaly_lower_range"
NEG_ANOMALY_UPPER_RANGE = "neg_anomaly_upper_range"
NEG_ANOMALY_LOWER_RANGE = "neg_anomaly_lower_range"
PROBABILITY = "probability"
AFTER_N_ITERATIONS = "after_n_iterations"
AVERAGE_DRIFT_RATE = "average_drift_rate"
VARIATION_RANGE = "variation_range"

# UI map for sensor errors (used for displaying error settings in the UI)
SENSOR_ERRORS_UI_MAP = {
    "type": "Type",
    ANOMALY: "Anomaly",
    MCAR: "Missing Completely At Random (MCAR)",
    DUPLICATE_DATA: "Duplicate Data",
    DRIFT: "Drift",
    PROBABILITY_POS_ANOMALY: "Probability for positive anomaly",
    PROBABILITY_NEG_ANOMALY: "Probability for negative anomaly",
    POS_ANOMALY_UPPER_RANGE: "Upper limit for positive anomaly",
    POS_ANOMALY_LOWER_RANGE: "Lower limit for positive anomaly",
    NEG_ANOMALY_UPPER_RANGE: "Upper limit for negative anomaly",
    NEG_ANOMALY_LOWER_RANGE: "Lower limit for negative anomaly",
    PROBABILITY: "Probability",
    AFTER_N_ITERATIONS: "After n iterations",
    AVERAGE_DRIFT_RATE: "Average drift rate",
    VARIATION_RANGE: "Variation range"
}