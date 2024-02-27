# Python program for Complex Code of Percentiles

def percentile(pth, total):
    """
    This function returns the position of a value based on the percentile
    and total number of values in the data
    """
    # Convert percentile to a decimal value
    percentile_decimal = pth / 100
    
    # Calculate the position of the value in the data
    position = percentile_decimal * total
    
    return position

