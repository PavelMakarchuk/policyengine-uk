from typing import Any, Callable
from openfisca_core.model_api import *
from openfisca_uk.entities import *
import numpy as np
from datetime import datetime
from pathlib import Path

DATA_FOLDER = Path(__file__).parent.parent / "data"

np.random.seed(0)


def add(entity, period, variable_names, options=None):
    """Sums a list of variables over entities.

    Args:
        entity (Entity): Either person, benunit or household
        period (Period): The period to calculate over
        variable_names (list): A list of variable names
        options (list, optional): The options to use - ADD, DIVIDE or MATCH to define period mismatch behaviour. Defaults to None.

    Returns:
        Array: Array of entity values.
    """
    return sum(
        map(lambda var: entity(var, period, options=options), variable_names)
    )


def aggr(entity, period, variable_names, options=None):
    """Sums a list of variables over each member of a group.

    Args:
        entity (Entity): Either benunit or household
        period (Period): The period to calculate over
        variable_names (list): A list of variable names
        options (list, optional): The options to use - ADD, DIVIDE or MATCH to define period mismatch behaviour. Defaults to None.

    Returns:
        Array: Array of entity values.
    """
    return sum(
        map(
            lambda var: entity.sum(
                entity.members(var, period, options=options)
            ),
            variable_names,
        )
    )


def aggr_max(entity, period, variable_names, options=None):
    """Finds the maximum of a list of variables over each member of a group.

    Args:
        entity (Entity): Either benunit or household
        period (Period): The period to calculate over
        variable_names (list): A list of variable names
        options (list, optional): The options to use - ADD, DIVIDE or MATCH to define period mismatch behaviour. Defaults to None.

    Returns:
        Array: Array of entity values.
    """
    return sum(
        map(
            lambda var: entity.max(
                entity.members(var, period, options=options)
            ),
            variable_names,
        )
    )


def select(conditions, choices):
    """Selects the corresponding choice for the first matching condition in a list.

    Args:
        conditions (list): A list of boolean arrays
        choices (list): A list of arrays

    Returns:
        Array: Array of values
    """
    return np.select(conditions, choices)


clip = np.clip
inf = np.inf

WEEKS_IN_YEAR = 52
MONTHS_IN_YEAR = 12


def amount_over(amount, threshold):
    return max_(0, amount - threshold)


def amount_between(amount, threshold_1, threshold_2):
    return clip(amount, threshold_1, threshold_2) - threshold_1


def random(entity, reset=True):
    x = np.random.rand(entity.count)
    if reset:
        np.random.seed(0)
    return x


def is_in(values, *targets):
    return sum(map(lambda target: values == target, targets))

def parameter_string_to_value(parameter_string, parameters, period):
    node = parameters(period)
    for name in parameter_string.split("."):
        node = getattr(node, name)
    return node

def rolls_over(uprating_parameter: str = None):
    def get_uprating_variable(cls):
        new_variable = type(cls.__name__, (cls,), {})
        if cls.__name__ == "pension_income":
            print()
        def formula(entity, period, parameters):
            original_output = cls.formula(entity, period, parameters)
            if np.all(original_output == 0):
                # no inputs, so uprate from previous year
                last_year_output = formula(entity, period.last_year, parameters)
                if uprating_parameter is not None:
                    last_year_value = parameter_string_to_value(uprating_parameter, parameters, period.last_year)
                    current_year_value = parameter_string_to_value(uprating_parameter, parameters, period)
                    multiplier = current_year_value / last_year_value
                else:
                    multiplier = 1
                return last_year_output * multiplier
            else:
                return original_output
        new_variable.formula = formula
        return new_variable
    return get_uprating_variable
