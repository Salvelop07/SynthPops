"""
This module provides functions that process data tables from the US Census
Bureau into simple distribution tables that SynthPops functions can talk to.

Also includes functions to process data tables from the National survey on
Long Term Care Providers in the US to convert those into rates by age for
each US state using SynthPops functions.

"""

import numpy as np
import pandas as pd
# import synthpops as sp
from . import base as spb
from . import data_distributions as spdata
from glob import glob as ls
import os


def process_us_census_age_counts(datadir, location, state_location, country_location, year, acs_period):
    """
    Process American Community Survey data for a given year to get an age count
    for the location binned into 18 age brackets.

    Args:
        datadir (str)          : file path to the data directory
        location (str)         : name of the location
        state_location (str)   : name of the state the location is in
        country_location (str) : name of the country the location is in
        year (int)             : the year for the American Community Survey
        acs_period (int)       : the number of years for the American Community Survey

    Returns:
        A dictionary with the binned age count and a dictionary with the age
        bracket ranges.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'age_distributions')
    file_path = os.path.join(file_path, f'ACSST{acs_period}Y{year}.S0101_data_with_overlays_{location}.csv')

    df = pd.read_csv(file_path)

    columns = [f'S0101_C01_00{i:d}E' for i in range(2, 10)] + [f'S0101_C01_0{i:d}E' for i in range(10, 20)]

    age_brackets = {}
    for b in np.arange(0, len(columns) - 1):
        age_brackets[b] = np.arange(5 * b, 5 * (b + 1))
    age_brackets[len(age_brackets)] = np.arange(5 * len(age_brackets), 101)

    age_bracket_count = {}
    for b in age_brackets:
        c = columns[b]
        try:
            try:
                count = int(df.loc[df['NAME'] == location][c].values[0])
            except:
                count = int(df.loc[df['NAME'] == location.replace('_', ' ')][c].values[0])
        except:
            try:
                count = float(df.loc[df['NAME'] == location][c].values[0])
            except:
                count = float(df.loc[df['NAME'] == location.replace('_', ' ')][c].values[0])
        age_bracket_count[b] = count

    return age_bracket_count, age_brackets


def process_us_census_age_counts_by_gender(datadir, location, state_location, country_location, year, acs_period):
    """
    Process American Community Survey data for a given year to get an age count
    by gender for the location binned into 18 age brackets.

    Args:
        datadir (str)          : file path to the data directory
        location (str)         : name of the location
        state_location (str)   : name of the state the location is in
        country_location (str) : name of the country the location is in
        year (int)             : the year for the American Community Survey
        acs_period (int)       : the number of years for the American Community Survey

    Returns:
        A dictionary with the binned age count by gender and a dictionary with
        the age bracket ranges.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'age_distributions')
    file_path = os.path.join(file_path, f'ACSST{acs_period}Y{year}.S0101_data_with_overlays_{location}.csv')

    df = pd.read_csv(file_path)

    columns_male = [f'S0101_C03_00{i:d}E' for i in range(2, 10)] + [f'S0101_C03_0{i:d}E' for i in range(10, 20)]
    columns_female = [col.replace('C03', 'C05') for col in columns_male]

    age_brackets = {}
    for b in range(0, len(columns_male) - 1):
        age_brackets[b] = np.arange(5 * b, 5 * (b + 1))
    age_brackets[len(age_brackets)] = np.arange(5 * len(age_brackets), 101)

    age_bracket_count_by_gender = {g: {} for g in ['male', 'female']}
    for b in age_brackets:
        mc = columns_male[b]
        fc = columns_female[b]
        try:
            mcount = int(df.loc[df['NAME'] == location][mc].values[0])
            fcount = int(df.loc[df['NAME'] == location][fc].values[0])
        except:
            mcount = int(df.loc[df['NAME'] == location.replace('_', ' ')][mc].values[0])
            fcount = int(df.loc[df['NAME'] == location.replace('_', ' ')][fc].values[0])
        age_bracket_count_by_gender['male'][b] = mcount
        age_bracket_count_by_gender['female'][b] = fcount

    return age_bracket_count_by_gender, age_brackets


def process_us_census_population_size(datadir, location, state_location, country_location, year, acs_period):
    """
    Process American Community Survey data for a given year to get the
    population size for the location.

    Args:
        datadir (str)          : file path to the data directory
        location (str)         : name of the location
        state_location (str)   : name of the state the location is in
        country_location (str) : name of the country the location is in
        year (int)             : the year for the American Community Survey
        acs_period (int)       : the number of years for the American Community Survey

    Returns:
        int: The population size of the location for a given year estimated from
        the American Community Survey.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'age_distributions')
    file_path = os.path.join(file_path, f'ACSST{acs_period}Y{year}.S0101_data_with_overlays_{location}.csv')

    df = pd.read_csv(file_path)
    try:
        population_size = int(df.loc[df['NAME'] == location]['S0101_C01_001E'].values[0])
    except:
        population_size = int(df.loc[df['NAME'] == location.replace('_', ' ')]['S0101_C01_001E'].values[0])
    return population_size


def process_us_census_household_size_count(datadir, location, state_location, country_location, year, acs_period):
    """
    Process American Community Survey data for a given year to get a household
    size count for the location. The last bin represents households of size 7 or
    higher.

    Args:
        datadir (str)          : file path to the data directory
        location (str)         : name of the location
        state_location (str)   : name of the state the location is in
        country_location (str) : name of the country the location is in
        year (int)             : the year for the American Community Survey
        acs_period (int)       : the number of years for the American Community Survey

    Returns:
        A dictionary with the household size count.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'household_size_distributions')
    file_path = os.path.join(file_path, f'ACSDT{acs_period}Y{year}.B11016_data_with_overlays_{location}.csv')

    df = pd.read_csv(file_path)

    household_size_count = dict.fromkeys(np.arange(1, 8), 0)
    try:
        household_size_count[1] = int(df.loc[df['NAME'] == location]['B11016_010E'].values[0])
    except:
        household_size_count[1] = int(df.loc[df['NAME'] == location.replace('_', ' ')]['B11016_010E'].values[0])
    for s in range(2, 8):
        try:
            household_size_count[s] = int(df.loc[df['NAME'] == location][f'B11016_00{(s+1):d}E'].values[0]) + int(df.loc[df['NAME'] == location][f'B11016_0{(s+9):d}E'].values[0])
        except:
            household_size_count[s] = int(df.loc[df['NAME'] == location.replace('_', ' ')][f'B11016_00{(s+1):d}E'].values[0]) + int(df.loc[df['NAME'] == location.replace('_', ' ')][f'B11016_0{(s+9):d}E'].values[0])

    return household_size_count


def process_us_census_employment_rates(datadir, location, state_location, country_location, year, acs_period):
    """
    Process American Community Survey data for a given year to get employment
    rates by age as a fraction.

    Args:
        datadir (str)          : file path to the data directory
        location (str)         : name of the location
        state_location (str)   : name of the state the location is in
        country_location (str) : name of the country the location is in
        year (int)             : the year for the American Community Survey
        acs_period (int)       : the number of years for the American Community Survey

    Returns:
        A dictionary with the employment rates by age as a fraction.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'employment')
    file_path = os.path.join(file_path, f'ACSST{acs_period}Y{year}.S2301_data_with_overlays_{location}.csv')

    df = pd.read_csv(file_path)
    columns = {i: f'S2301_C03_00{i:d}E' for i in range(2, 10)}
    for i in range(10, 12):
        columns[i] = f'S2301_C03_0{i:d}E'
    column_age_ranges = {}
    column_age_ranges[2] = np.arange(16, 20)
    column_age_ranges[3] = np.arange(20, 25)
    column_age_ranges[4] = np.arange(25, 30)
    column_age_ranges[5] = np.arange(30, 35)
    column_age_ranges[6] = np.arange(35, 45)
    column_age_ranges[7] = np.arange(45, 55)
    column_age_ranges[8] = np.arange(55, 60)
    column_age_ranges[9] = np.arange(60, 65)
    column_age_ranges[10] = np.arange(65, 75)
    column_age_ranges[11] = np.arange(75, 101)

    employment_rates = dict.fromkeys(np.arange(16, 101), 0)
    for i in column_age_ranges:
        for a in column_age_ranges[i]:
            try:
                employment_rates[a] = float(df.loc[df['NAME'] == location][columns[i]].values[0]) / 100.
            except:
                employment_rates[a] = float(df.loc[df['NAME'] == location.replace('_', ' ')][columns[i]].values[0]) / 100.
    return employment_rates


def process_us_census_enrollment_rates(datadir, location, state_location, country_location, year, acs_period):
    """
    Process American Community Survey data for a given year to get enrollment
    rates by age as a fraction.

    Args:
        datadir (str)          : file path to the data directory
        location (str)         : name of the location
        state_location (str)   : name of the state the location is in
        country_location (str) : name of the country the location is in
        year (int)             : the year for the American Community Survey
        acs_period (int)       : the number of years for the American Community Survey

    Returns:
        A dictionary with the enrollment rates by age as a fraction.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'enrollment')
    file_path = os.path.join(file_path, f'ACSST{acs_period}Y{year}.S1401_data_with_overlays_{location}.csv')

    df = pd.read_csv(file_path)
    columns = {i: f'S1401_C02_0{i:d}E' for i in np.arange(14, 30, 2)}
    column_age_ranges = {}
    column_age_ranges[14] = np.arange(3, 5)
    column_age_ranges[16] = np.arange(5, 10)
    column_age_ranges[18] = np.arange(10, 15)
    column_age_ranges[20] = np.arange(15, 18)
    column_age_ranges[22] = np.arange(18, 20)
    column_age_ranges[24] = np.arange(20, 25)
    column_age_ranges[26] = np.arange(25, 35)
    column_age_ranges[28] = np.arange(35, 51)

    enrollment_rates = dict.fromkeys(np.arange(101), 0)
    for i in column_age_ranges:
        for a in column_age_ranges[i]:
            try:
                enrollment_rates[a] = float(df.loc[df['NAME'] == location][columns[i]].values[0]) / 100.
            except:
                enrollment_rates[a] = float(df.loc[df['NAME'] == location.replace('_', ' ')][columns[i]].values[0]) / 100.
    return enrollment_rates


def process_usa_long_term_care_facility_rates_by_age(datadir, state_location, country_location):
    """
    Process the National Long Term Care Providers state data tables from 2016 to
    get the estimated user rates by age.

    Args:
        datadir (string)          : file path to the data directory
        state_location (string)   : name of the state
        country_location (string) : name of the country the state is in

    Returns:
        dict: A dictionary with the estimated rates of Long Term Care Facility
        usage by age for the state in 2016.

    """

    year = 2016  # use 2016 data to match the year of data for the LTCF state data table
    acs_period = 1  # using ACS 1 year estimates
    part = 2  # which part of the LTCF state data table to use

    ltcf_df = spdata.get_usa_long_term_care_facility_data(datadir, state_location, country_location, part=part)
    ltcf_age_bracket_keys = ['Under 65', '65–74', '75–84', '85 and over']  # age brackets as defined by National LTCF Providers survey

    facility_keys = ['Nursing home',
                     'Residential care community',
                     # 'Hospice',  # Hospice users are often cared for in their own homes so it may not be appropriate to include them in facility resident numbers.
                     ]
    facility_users = {}

    # 2016 state wide age breakdown of LTCF users
    facility_user_age_percentage = {}
    for fk in facility_keys:
        facility_users[fk] = {}
        facility_user_age_percentage[fk] = {}
        facility_users[fk]['Total'] = int(ltcf_df[ltcf_df.iloc[:, 0] == 'Number of users2, 5'][fk].values[0].replace(',', ''))
        for ab in ltcf_age_bracket_keys:
            facility_user_age_percentage[fk][ab] = float(ltcf_df[ltcf_df.iloc[:, 0] == ab][fk].values[0].replace(',', '')) / 100.

    # 2016 state wide total LTCF users by facility type and age brackets
    for fk in facility_keys:
        for ab in ltcf_age_bracket_keys:
            facility_users[fk][ab] = facility_users[fk]['Total'] * facility_user_age_percentage[fk][ab]

    # map the LTCF users age groups to the census age groups
    age_group_mapping = {'Under 65': '60-64', '65–74': '65-74', '75–84': '75-84', '85 and over': '85-100'}
    age_brackets = spdata.get_census_age_brackets(datadir, state_location=state_location, country_location=country_location, nbrackets=18)
    age_by_brackets_dic = spb.get_age_by_brackets_dic(age_brackets)

    brackets_in_range_mapping = {}
    for ab in ltcf_age_bracket_keys:
        sa, ea = age_group_mapping[ab].split('-')
        sa, ea = int(sa), int(ea)
        age_range = np.arange(sa, ea + 1)
        brackets_in_range = set()
        for a in age_range:
            b = age_by_brackets_dic[a]
            brackets_in_range.add(b)
        brackets_in_range_mapping[ab] = sorted(brackets_in_range.copy())

    # 2016 state population size
    population_size = process_us_census_population_size(datadir, state_location, state_location, country_location, year, acs_period)

    # 2016 state age distribution (18 age brackets)
    age_bracket_distr, age_brackets = process_us_census_age_counts(datadir, state_location, state_location, country_location, year, acs_period)
    age_bracket_distr = spb.norm_dic(age_bracket_distr)

    age_bracket_count = {}
    for b in sorted(age_bracket_distr.keys()):
        age_bracket_count[b] = population_size * age_bracket_distr[b]

    # 2016 state age count for the LTCF data defined age brackets
    state_older_age_counts = {}
    for ab in ltcf_age_bracket_keys:
        state_older_age_counts[ab] = 0
        for b in brackets_in_range_mapping[ab]:
            state_older_age_counts[ab] += age_bracket_distr[b] * population_size

    # calculate the percent using facilities by the LTCF data age brackets
    ltcf_rates_by_age = dict.fromkeys(np.arange(101), 0)

    for ab in ltcf_age_bracket_keys:
        ltcf_rates_by_age[ab] = np.sum([facility_users[fk][ab] for fk in facility_keys]) / state_older_age_counts[ab]

        for b in brackets_in_range_mapping[ab]:
            for a in age_brackets[b]:
                ltcf_rates_by_age[a] = ltcf_rates_by_age[ab].copy()

    for ab in ltcf_age_bracket_keys:
        ltcf_rates_by_age.pop(ab, None)

    return ltcf_rates_by_age


def write_age_bracket_distr_18(datadir, location_alias, state_location, country_location, age_bracket_count, age_brackets):
    """
    Write age bracket distribution binned to 18 age brackets.

    Args:
        datadir (str)            : file path to the data directory
        location_alias (str)     : more commonly known name of the location
        state_location (str)     : name of the state the location is in
        country_location (str)   : name of the country the location is in
        age_bracket_count (dict) : dictionary of the age count given by 18 brackets
        age_brackets (dict)      : dictionary of the age range for each bracket

    Returns:
        None.
    """
    age_bracket_distr = spb.norm_dic(age_bracket_count)
    file_path = os.path.join(datadir, country_location, state_location, 'age_distributions')
    os.makedirs(file_path, exist_ok=True)
    file_name = os.path.join(file_path, f'{location_alias}_age_bracket_distr_18.dat')
    f = open(file_name, 'w')
    f.write('age_bracket,percent\n')
    for b in sorted(age_brackets.keys()):
        s = age_brackets[b][0]
        e = age_brackets[b][-1]
        f.write(f'{s:d}_{e:d},{age_bracket_distr[b]:.16f}\n')
    f.close()


def write_age_bracket_distr_16(datadir, location_alias, state_location, country_location, age_bracket_count, age_brackets):
    """
    Write age bracket distribution binned to 16 age brackets.

    Args:
        datadir (str)            : file path to the data directory
        location_alias (str)     : more commonly known name of the location
        state_location (str)     : name of the state the location is in
        country_location (str)   : name of the country the location is in
        age_bracket_count (dict) : dictionary of the age count given by 18 brackets
        age_brackets (dict)      : dictionary of the age range for each bracket

    Returns:
        None.
    """
    age_bracket_distr = spb.norm_dic(age_bracket_count)
    file_path = os.path.join(datadir, country_location, state_location, 'age_distributions')
    os.makedirs(file_path, exist_ok=True)
    file_name = os.path.join(file_path, f'{location_alias}_age_bracket_distr_16.dat')
    f = open(file_name, 'w')
    f.write('age_bracket,percent\n')
    for b in range(15):
        s = age_brackets[b][0]
        e = age_brackets[b][-1]
        f.write(f'{s:d}_{e:d},{age_bracket_distr[b]:.16f}\n')
    f.write(f'{age_brackets[15][0]:d}_{age_brackets[max(age_brackets.keys())][-1]},{np.sum([age_bracket_distr[b] for b in range(15, len(age_bracket_distr))]):.16f}\n')
    f.close()


def write_gender_age_bracket_distr_18(datadir, location_alias, state_location, country_location, age_bracket_count_by_gender, age_brackets):
    """
    Write age bracket by gender distribution data binned to 18 age brackets.

    Args:
        datadir (str)            : file path to the data directory
        location_alias (str)     : more commonly known name of the location
        state_location (str)     : name of the state the location is in
        country_location (str)   : name of the country the location is in
        age_bracket_distr (dict) : dictionary of the age count by gender given by 18 brackets
        age_brackets (dict)      : dictionary of the age range for each bracket

    Returns:
        None.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'age_distributions')
    os.makedirs(file_path, exist_ok=True)
    file_name = os.path.join(file_path, f'{location_alias}_gender_fraction_by_age_bracket_18.dat')
    f = open(file_name, 'w')
    f.write('age_bracket,fraction_male,fraction_female\n')
    for b in sorted(age_brackets.keys()):
        s = age_brackets[b][0]
        e = age_brackets[b][-1]
        mcount = age_bracket_count_by_gender['male'][b]
        fcount = age_bracket_count_by_gender['female'][b]
        mfrac = float(mcount) / (mcount + fcount)
        ffrac = float(fcount) / (mcount + fcount)
        f.write(f'{s:d}_{e:d},{mfrac:.16f},{ffrac:.16f}\n')
    f.close()


def write_gender_age_bracket_distr_16(datadir, location_alias, state_location, country_location, age_bracket_count_by_gender, age_brackets):
    """
    Write age bracket by gender distribution binned to 16 age brackets.

    Args:
        datadir (str)            : file path to the data directory
        location_alias (str)     : more commonly known name of the location
        state_location (str)     : name of the state the location is in
        country_location (str)   : name of the country the location is in
        age_bracket_distr (dict) : dictionary of the age count by gender given by 18 brackets
        age_brackets (dict)      : dictionary of the age range for each bracket

    Returns:
        None.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'age_distributions')
    os.makedirs(file_path, exist_ok=True)
    file_name = os.path.join(file_path, f'{location_alias}_gender_fraction_by_age_bracket_16.dat')
    f = open(file_name, 'w')
    f.write('age_bracket,fraction_male,fraction_female\n')
    for b in range(15):
        s = age_brackets[b][0]
        e = age_brackets[b][-1]
        mcount = age_bracket_count_by_gender['male'][b]
        fcount = age_bracket_count_by_gender['female'][b]
        mfrac = float(mcount) / (mcount + fcount)
        ffrac = float(fcount) / (mcount + fcount)
        f.write(f'{s:d}_{e:d},{mfrac:.16f},{ffrac:.16f}\n')
    s = age_brackets[15][0]
    e = age_brackets[max(age_brackets.keys())][-1]
    mcount = np.sum([age_bracket_count_by_gender['male'][b] for b in range(15, len(age_brackets))])
    fcount = np.sum([age_bracket_count_by_gender['female'][b] for b in range(15, len(age_brackets))])
    mfrac = float(mcount) / (mcount + fcount)
    ffrac = float(fcount) / (mcount + fcount)
    f.write(f'{s:d}_{e:d},{mfrac:.16f},{ffrac:.16f}\n')
    f.close()


def read_household_size_count(datadir, location_alias, state_location, country_location):
    """
    Get household size count dictionary.

    Args:
        datadir (str)          : file path to the data directory
        location_alias (str)   : more commonly known name of the location
        state_location (str)   : name of the state the location is in
        country_location (str) : name of the country the location is in

    Returns:
        dict: A dictionary of the household size count.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'household_size_distributions')
    file_name = os.path.join(file_path, f'{location_alias}_household_size_count.dat')
    df = pd.read_csv(file_name, delimiter=',')
    return dict(zip(df.household_size, df.size_count))


def write_household_size_count(datadir, location_alias, state_location, country_location, household_size_count):
    """
    Write household size count.

    Args:
        datadir (str)               : file path to the data directory
        location_alias (str)        : more commonly known name of the location
        state_location (str)        : name of the state the location is in
        country_location (str)      : name of the country the location is in
        household_size_count (dict) : dictionary of the household size count.

    Returns:
        None.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'household_size_distributions')
    os.makedirs(file_path, exist_ok=True)
    file_name = os.path.join(file_path, f'{location_alias}_household_size_count.dat')
    f = open(file_name, 'w')
    f.write('household_size,size_count\n')
    for s in sorted(household_size_count.keys()):
        f.write(f'{s:d},{household_size_count[s]:d}\n')
    f.close()


def write_household_size_distr(datadir, location_alias, state_location, country_location, household_size_count):
    """
    Write household size distribution.

    Args:
        datadir (str)               : file path to the data directory
        location_alias (str)        : more commonly known name of the location
        state_location (str)        : name of the state the location is in
        country_location (str)      : name of the country the location is in
        household_size_count (dict) : dictionary of the household size count.

    Returns:
        None.
    """
    household_size_distr = spb.norm_dic(household_size_count)
    file_path = os.path.join(datadir, country_location, state_location, 'household_size_distributions')
    os.makedirs(file_path, exist_ok=True)
    file_name = os.path.join(file_path, f'{location_alias}_household_size_distr.dat')
    f = open(file_name, 'w')
    f.write('household_size,percent\n')
    for s in sorted(household_size_count.keys()):
        # f.write('%i' % s + ',' + '%.16f' % household_size_distr[s] + '\n')
        f.write(f'{s:d},{household_size_distr[s]:.16f}\n')

    f.close()


def write_employment_rates(datadir, location_alias, state_location, country_location, employment_rates):
    """
    Write employment rates by age as a fraction.

    Args:
        datadir (str)           : file path to the data directory
        location_alias (str)    : more commonly known name of the location
        state_location (str)    : name of the state the location is in
        country_location (str)  : name of the country the location is in
        employment_rates (dict) : dictionary of the employment rates by age as a fraction.

    Returns:
        None.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'employment')
    os.makedirs(file_path, exist_ok=True)
    file_name = os.path.join(file_path, f'{location_alias}_employment_rates_by_age.dat')
    f = open(file_name, 'w')
    f.write('Age,Percent\n')
    for a in sorted(employment_rates.keys()):
        f.write(f'{a:d},{employment_rates[a]:.3f}\n')
    f.close()


def write_enrollment_rates(datadir, location_alias, state_location, country_location, enrollment_rates):
    """
    Write employment rates by age as a fraction.

    Args:
        datadir (str)           : file path to the data directory
        location_alias (str)    : more commonly known name of the location
        state_location (str)    : name of the state the location is in
        country_location (str)  : name of the country the location is in
        enrollment_rates (dict) : dictionary of the enrollment rates by age as a fraction.

    Returns:
        None.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'enrollment')
    os.makedirs(file_path, exist_ok=True)
    file_name = os.path.join(file_path, f'{location_alias}_enrollment_rates_by_age.dat')
    f = open(file_name, 'w')
    f.write('Age,Percent\n')
    for a in sorted(enrollment_rates.keys()):
        f.write(f'{a:d},{enrollment_rates[a]:.3f}\n')
    f.close()


def write_long_term_care_facility_use_rates(datadir, state_location, country_location, ltcf_rates_by_age):
    """
    Write Long Term Care Facility usage rates by age as a fraction for a state
    in the United States.

    Args:
        datadir (str)            : file path to the data directory
        location_alias (str)     : more commonly known name of the location
        state_location (str)     : name of the state the location is in
        country_location (str)   : name of the country the location is in
        ltcf_rates_by_age (dict) : dictionary of the long term care facility use rates by age as a fraction.

    Returns:
        None.
    """
    file_path = os.path.join(datadir, country_location, state_location, 'assisted_living')
    os.makedirs(file_path, exist_ok=True)
    file_name = os.path.join(file_path, f'{state_location}_long_term_care_facility_use_rates_by_age.dat')
    f = open(file_name, 'w')
    f.write('Age,Percent\n')
    for a in sorted(ltcf_rates_by_age.keys()):
        f.write(f'{a:d},{ltcf_rates_by_age[a]:.8f}\n')
    f.close()
