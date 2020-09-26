from openfisca_core.model_api import *
from openfisca_uk.entities import *
import numpy as np


class is_male(Variable):
    value_type = bool
    entity = Person
    label = u"Whether the person is male (False if female)"
    definition_period = ETERNITY


class is_head(Variable):
    value_type = bool
    entity = Person
    label = u"label"
    definition_period = ETERNITY


class is_state_pension_age(Variable):
    value_type = bool
    entity = Person
    label = u"Whether the person is State Pension age"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        return person("is_male", period) * (
            person("age", period)
            >= parameters(period).benefits.state_pension.male_state_pension_age
        ) + (1 - person("is_male", period)) * (
            person("age", period)
            >= parameters(
                period
            ).benefits.state_pension.female_state_pension_age
        )


class disabled(Variable):
    value_type = bool
    entity = Person
    label = u"Whether disabled"
    definition_period = ETERNITY


class adult_weight(Variable):
    value_type = float
    entity = Person
    label = u"FRS weighting of the person if they are an adult, 0 if a child (none provided by the FRS)"
    definition_period = ETERNITY


class age_band(Variable):
    value_type = int
    entity = Person
    label = u"FRS-encoded age band"
    definition_period = ETERNITY


class is_CTC_child_limit_exempt(Variable):
    value_type = bool
    entity = Person
    label = u"Whether the child was born after 2017 and therefore exempt from the two-child limit for Child Tax Credit"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        return (person("age", period) >= 3) * (1 - person("is_adult", period))


class is_senior(Variable):
    value_type = bool
    entity = Person
    label = u"Whether the person is over retirement age"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        return person("age", period) >= 65


class is_adult(Variable):
    value_type = bool
    entity = Person
    label = u"Whether the person is working age"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        return (person("age", period) >= 18) * (person("age", period) < 65)


class is_child(Variable):
    value_type = bool
    entity = Person
    label = u"Whether the person is under working age"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        return person("age", period) < 18


class hours_worked(Variable):
    value_type = float
    entity = Person
    label = u"Total hours worked per week"
    definition_period = ETERNITY


class age(Variable):
    value_type = int
    entity = Person
    label = u"Likely age from FRS codes"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        band = person("age_band", period)
        AGES = [0, 5, 10, 16, 23, 27, 33, 37, 43, 47, 53, 57, 63, 67, 73, 80]
        return sum(map(lambda i: (band == i) * AGES[i - 1], range(1, 17)))


class is_young_child(Variable):
    value_type = bool
    entity = Person
    label = u"Whether the person is under 14"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        return person("age", period) < 14


class is_older_child(Variable):
    value_type = bool
    entity = Person
    label = u"Whether the person is over 14 but under 18"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        return (person("age", period) >= 14) * (person("age", period) < 18)
