def calculate_risk(percent_change, low_threshold=2.0, high_threshold=5.0):
    """
    Classify coastal change risk based on percentage change.

    MVP thresholds:
        < 2%       -> Low
        2% to 5%   -> Medium
        > 5%       -> High

    Absolute percentage change is used so that both
    erosion (negative) and accretion (positive) are
    evaluated by magnitude.

    These thresholds are hackathon MVP thresholds and
    are not scientifically validated coastal-risk thresholds.
    """

    change = abs(percent_change)

    if change < low_threshold:
        return "Low"

    elif change <= high_threshold:
        return "Medium"

    else:
        return "High"


if __name__ == "__main__":

    # Test cases
    test_values = [-1.5, -2.0, -4.02, 5.0, 6.0, 3.5]

    for percent_change in test_values:

        risk = calculate_risk(percent_change)

        print(
            f"{percent_change}% change -> {risk} risk"
        )