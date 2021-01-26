import json
from jsonobject import *


class SchoolSizeDistributionByType(JsonObject):
    school_type = StringProperty()
    # length should be len(location.school_size_distribution)
    size_distribution = ListProperty(FloatProperty)


class SchoolTypeByAge(JsonObject):
    school_type = StringProperty()
    # [min_age, max_age]
    age_range = ListProperty(FloatProperty)


class Location(JsonObject):
    data_provenance_notices = ListProperty(StringProperty)
    reference_links = ListProperty(StringProperty)
    citations = ListProperty(StringProperty)

    population_age_distribution = ListProperty(
        # [min_age, max_age, percentage]
        ListProperty(FloatProperty)
    )

    employment_rates_by_age = ListProperty(
        # [age, percentage]
        ListProperty(FloatProperty)
    )

    enrollment_rates_by_age = ListProperty(
        # [age, percentage]
        ListProperty(FloatProperty)
    )

    household_head_age_brackets = ListProperty(
        # [age_min, age_max]
        ListProperty(FloatProperty)
    )

    household_head_age_distribution_by_family_size = ListProperty(
        # length should be len(household_head_age_brackets) + 1
        # The first entry is the family size, the rest of the entries fill in the household head age counts for
        # each household head age bracket.
        # [family_size, count_1, count_2, ...]
        ListProperty(FloatProperty)
    )

    household_size_distribution = ListProperty(
        # [size, percentage]
        ListProperty(FloatProperty)
    )

    ltcf_resident_to_staff_ratio_distribution = ListProperty(
        # [ratio_low, ratio_hi, percentage]
        ListProperty(FloatProperty)
    )

    ltcf_num_residents_distribution = ListProperty(
        # [num_residents_low, num_residents_hi, percentage]
        ListProperty(FloatProperty)
    )

    ltcf_num_staff_distribution = ListProperty(
        # [num_staff_low, num_staff_hi, percentage]
        ListProperty(FloatProperty)
    )

    school_size_brackets = ListProperty(
        # [school_size_low, school_size_hi]
        ListProperty(FloatProperty)
    )

    school_size_distribution = ListProperty(FloatProperty)

    # The length of size_distribution needs to equal the length of school_size_brackets
    school_size_distribution_by_type = ListProperty(SchoolSizeDistributionByType)

    school_types_by_age = ListProperty(SchoolTypeByAge)

    workplace_size_counts_by_num_personnel = ListProperty(
        # [num_personnel_low, num_personnel_hi, count]
        ListProperty(FloatProperty)
    )


def load_location_from_json(json_obj):
    location = Location(json_obj)
    check_location_constraints_satisfied(location)
    return location


def load_location_from_json_str(json_str):
    json_obj = json.loads(json_str)
    return load_location_from_json(json_obj)


def load_location_from_filepath(filepath):
    f = open(filepath, 'r')
    json_obj = json.load(f)
    return load_location_from_json(json_obj)


def check_location_constraints_satisfied(location):
    """
    Checks a number of constraints that need to be satisfied, above and
    beyond the schema.

    Args:
        location:

    Returns:
        Nothing

    Raises:
        RuntimeError with a description if one of the constraints is
        not satisfied.

    """
    [status, msg] = are_location_constraints_satisfied(location)
    if not status:
        raise RuntimeError(msg)


def are_location_constraints_satisfied(location):
    """
    Checks a number of constraints that need to be satisfied, above and
    beyond the schema.

    Args:
        location:

    Returns:
        [True, None] If all constraints are satisfied.
        [False, string] If a constraint is violated.

    """

    for f in [check_population_age_distribution,
              check_employment_rates_by_age,
              check_enrollment_rates_by_age,
              check_household_age_brackets,
              check_household_head_age_distributions_by_family_size,
              check_household_size_distribution,
              check_ltcf_resident_to_staff_ratio_distribution,
              check_ltcf_num_residents_distribution,
              check_ltcf_num_staff_distribution,
              check_school_size_brackets,
              check_school_size_distribution,
              check_school_size_distribution_by_type,
              check_school_types_by_age,
              check_workplace_size_counts_by_num_personnel,
              ]:
        [status, msg] = f(location)
        if not status:
            return [status, msg]

    return [True, None]


def check_array_of_arrays_entry_lens(location, expected_len, property_name):
    arr = getattr(location, property_name)
    for [k, bracket] in enumerate(arr):
        if not len(bracket) == expected_len:
            return [False,
                    f"Entry [{k}] in {property_name} has invalid length: [{len(bracket)}]; should be [{expected_len}]"]
    return [True, None]


def check_population_age_distribution(location):
    return check_array_of_arrays_entry_lens(location, 3, 'population_age_distribution')


def check_employment_rates_by_age(location):
    return check_array_of_arrays_entry_lens(location, 2, 'employment_rates_by_age')


def check_enrollment_rates_by_age(location):
    return check_array_of_arrays_entry_lens(location, 2, 'enrollment_rates_by_age')


def check_household_age_brackets(location):
    return check_array_of_arrays_entry_lens(location, 2, 'household_head_age_brackets')


def check_household_head_age_distributions_by_family_size(location):
    num_household_age_brackets = len(location.household_head_age_brackets)

    for [k, household_head_age_distribution] in enumerate(location.household_head_age_distribution_by_family_size):
        expected_len = 1 + num_household_age_brackets
        actual_len = len(household_head_age_distribution)
        if not actual_len == expected_len:
            return [False, f"Entry [{k}] in household_head_age_distribution_by_family_size has invalid length: [{actual_len}]; should be [{expected_len}]"]
    return [True, None]


def check_household_size_distribution(location):
    return check_array_of_arrays_entry_lens(location, 2, 'household_size_distribution')


def check_ltcf_resident_to_staff_ratio_distribution(location):
    return check_array_of_arrays_entry_lens(location, 3, 'ltcf_resident_to_staff_ratio_distribution')


def check_ltcf_num_residents_distribution(location):
    return check_array_of_arrays_entry_lens(location, 3, 'ltcf_num_residents_distribution')


def check_ltcf_num_staff_distribution(location):
    return check_array_of_arrays_entry_lens(location, 3, 'ltcf_num_staff_distribution')


def check_school_size_brackets(location):
    return check_array_of_arrays_entry_lens(location, 2, 'school_size_brackets')


def check_school_size_distribution(location):
    return [True, None]


def check_school_size_distribution_by_type(location):
    num_school_size_brackets = len(location.school_size_brackets)

    for [k, bracket] in enumerate(location.school_size_distribution_by_type):
        expected_len = num_school_size_brackets
        actual_len = len(bracket.size_distribution)
        if not actual_len == num_school_size_brackets:
            return [False,
                    f"Entry [{k} - {bracket.school_type}] in school_size_distribution_by_type has invalid length for size_distribution: [{actual_len}]; should be [{expected_len}]"]
    return [True, None]


def check_school_types_by_age(location):
    for [k, bracket] in enumerate(location.school_types_by_age):
        expected_len = 2
        actual_len = len(bracket.age_range)
        if not actual_len == expected_len:
            return [False,
                    f"Entry [{k} - {bracket.school_type}] in school_types_by_age has invalid length for age_range: [{actual_len}]; should be [{expected_len}]"]
    return [True, None]


def check_workplace_size_counts_by_num_personnel(location):
    return check_array_of_arrays_entry_lens(location, 3, 'workplace_size_counts_by_num_personnel')