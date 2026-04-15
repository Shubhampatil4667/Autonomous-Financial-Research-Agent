from typing import Dict, Any, List
import numpy as np

def calculation_engine(operation: str, data: List[float]) -> Dict[str, Any]:
    """
    Perform financial calculations
    """
    if operation == "mean":
        result = np.mean(data)
    elif operation == "std":
        result = np.std(data)
    elif operation == "growth_rate":
        if len(data) > 1:
            result = (data[-1] - data[0]) / data[0] * 100
        else:
            result = 0.0
    elif operation == "compound_annual_growth":
        if len(data) > 1:
            years = len(data) - 1
            result = ((data[-1] / data[0]) ** (1/years) - 1) * 100
        else:
            result = 0.0
    else:
        result = 0.0

    return {
        "operation": operation,
        "input_data": data,
        "result": result,
        "description": f"{operation} calculation result: {result}"
    }