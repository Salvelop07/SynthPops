"""
Test that school sizes are being generated by school type when with_school_types is turned on and data is available.
"""

import sciris as sc
import synthpops as sp
import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
import cmasher as cmr
import cmocean
import pytest
import settings


# parameters to generate a test population
pars = sc.objdict(
    n                               = 5e1,
    rand_seed                       = 123,

    country_location                = 'usa',
    state_location                  = 'Washington',
    location                        = 'seattle_metro',
    use_default                     = True,

    smooth_ages                     = True,
    window_length                   = 7,
    household_method                = 'infer_ages',

    with_industry_code              = 0,
    with_facilities                 = 0,
    with_non_teaching_staff         = 1,
    use_two_group_reduction         = 1,
    with_school_types               = 1,

    school_mixing_type              = {'pk': 'age_and_class_clustered', 'es': 'age_and_class_clustered', 'ms': 'age_and_class_clustered', 'hs': 'random', 'uv': 'random'},  # you should know what school types you're working with
)


def test_empty_household():
    sp.logger.info("Test creating an empty household.")

    household = sp.Household()

    def check_phrase(key, value, passed):
        print(f"Check {'passed' if passed else 'failed'}. household {key} for an empty household is {value}.")
        assert passed

    check_phrase('hhid', household['hhid'], passed=household['hhid'] is None)
    check_phrase('reference_uid', household['reference_uid'], passed=household['reference_uid'] is None)
    check_phrase('reference_age', household['reference_age'], passed=household['reference_age'] is None)

    np.testing.assert_array_equal(household['member_uids'], np.array([], dtype=int), err_msg="Check failed: empty array not found for member_uids.", verbose=True)
    check_phrase('member_uids', household['member_uids'], passed=True)

    np.testing.assert_array_equal(household['member_ages'], np.array([], dtype=int), err_msg="Check failed: empty array not found for member_ages.", verbose=True)
    check_phrase('member_ages', household['member_ages'], passed=True)

    print('Checks passed for an empty household.')


def test_make_household():
    sp.logger.info("Test creating a household after the fact.")
    pop = sp.Pop(**pars)

    # we don't need to store this in the pop object but this shows that we can
    # and now the tests are being run using data stored in the pop object (pop.homes_by_uids, pop.age_by_uid)
    household = sp.Household()
    household.set_household(member_uids=pop.homes_by_uids[0], member_ages=[pop.age_by_uid[i] for i in pop.homes_by_uids[0]],
                            reference_uid=min(pop.homes_by_uids[0]), reference_age=pop.age_by_uid[min(pop.homes_by_uids[0])],
                            hhid=0)

    assert household['hhid'] == 0, f"Check failed. household hhid is {household['hhid']}."
    print('Check passed. household hhid is 0.')

    assert len(household['member_uids']) == len(household['member_ages']), 'Check failed: member_uids and member_ages have different lengths.'
    print(f"Check passed. household member_uids and member_ages have the same length ({len(household['member_uids'])}).")

    assert isinstance(household['member_uids'], np.ndarray), 'Check failed: member_uids is not a np.array.'
    print("Check passed. household member_uids is a np.array.")

    assert len(household) == len(household['member_uids']), 'Check failed: len(household) does not return the household size, i.e. the number of household members.'
    print('Check passed. len(household) returns the number of household members.')

    assert isinstance(household['member_ages'], np.ndarray), 'Check failed: member_ages is not a np.array.'
    print('Check passed. household member_ages is a np.array.')

    assert household['reference_uid'] is not None, 'Check failed. household reference_uid is None.'
    print(f"Check passed. household reference_uid is not None and instead is {household['reference_uid']}.")

    assert household['reference_age'] is not None, 'Check failed. household reference_age is None.'
    print(f"Check passed. household reference_age is not None and instead is {household['reference_age']}.")

    assert len(household), f"Check failed. household size is {len(household)}."
    print(f"Check passed. household household size is {len(household)}.")

    household_2 = sp.Household()
    household_2['member_uids'] = ['a']
    with pytest.raises(TypeError):
        household_2.validate()
    print('Check passed. A synthpops household must have member_uids that are passable as a np.array of ints.')

    household_2 = sp.Household()
    household_2['hhid'] = 'b'
    with pytest.raises(TypeError):
        household_2.validate()
    print('Check passed. A synthpops household must have hhid that is an int or None.')


def test_add_household():
    sp.logger.info("Test creating a sp.Household object and adding it to an empty sp.Households class after generation.")
    home = [1, 2, 3]
    age_by_uid = {1: 88, 2: 45, 3: 47}
    household = sp.Household(member_uids=home, member_ages=[age_by_uid[i] for i in home],
                             reference_uid=home[0], reference_age=age_by_uid[home[0]],
                             hhid=0)

    assert isinstance(household, sp.Household), 'Check failed. Not a sp.Household object.'

    pop = sc.prettyobj()
    pop.households = []
    sp.add_household(pop, household)

    assert isinstance(pop.households[0], sp.Household), 'Check failed. Did not add a sp.Household object to the list of households.'
    print('Check passed. Added a sp.Household object to an sp.Households object.')


def test_households_basic():
    sp.logger.info("Test creating generic households.")
    homes_by_uids = [[1, 2, 3], [4], [7, 6, 5, 8, 9]]
    age_by_uid = {1: 88, 2: 45, 3: 47, 4: 38, 5: 12, 6: 19, 7: 55, 8: 58, 9: 99}

    pop = sp.Pop(n=settings.pop_sizes.small)

    pop_2 = sc.prettyobj()
    pop_2.households = []
    sp.populate_households(pop_2, homes_by_uids, age_by_uid)


    # assert households.n_households == len(homes_by_uids), "number of households should match."
    assert pop_2.n_households == len(homes_by_uids), "number of households should match."
    for i in range(0, len(homes_by_uids)):
        assert pop_2.households[i]['reference_uid'] == homes_by_uids[i][0]
        assert sp.get_household(pop_2, i)['reference_age'] == age_by_uid[homes_by_uids[i][0]]
        assert len(pop_2.households[i]) == len(homes_by_uids[i])
        # assert households.get_household(i)['reference_uid'] == homes_by_uids[i][0]
        # assert households.get_household(i)['reference_age'] == age_by_uid[homes_by_uids[i][0]]
        # assert len(households.get_household(i)) == len(homes_by_uids[i])
    print('Check passed. Generic households can be populated during class initialization.')

    not_a_household = ''
    with pytest.raises(ValueError):
        sp.add_household(pop_2, not_a_household)
    print('Check passed. Cannot add an object that is not a sp.Household using sp.add_household().')

    with pytest.raises(TypeError):
        sp.get_household(pop_2, 0.5)
    print('Check passed. Cannot get a household with a non-int hhid')

    with pytest.raises(ValueError):
        sp.get_household(pop_2, len(pop_2.households) + 1)
    print('Check passed. Cannot get a household with hhid larger than the number of households')


@pytest.mark.skip  # necessary for vital dynamics but not working right now
def test_reset_household_values():
    sp.logger.info("Test resetting household values. Warning these features should only be available when synthpops is set to use vital dynamics.")
    homes_by_uids = [[1, 2, 3], [4], [7, 6, 5, 8, 9]]
    age_by_uid = {1: 88, 2: 45, 3: 47, 4: 38, 5: 12, 6: 19, 7: 55, 8: 58, 9: 99}
    pop = sc.prettyobj()
    pop.households = []
    sp.populate_households(pop, homes_by_uids, age_by_uid)

    # households.get_household(0).set_hhid(7)
    # households.get_household(0).set_member_uids([8, 8, 8])
    # households.get_household(0).set_member_ages([0, 0, 0])
    # households.get_household(0).set_reference_uid(8)
    # households.get_household(0).set_reference_age(0)


def test_households_initialization():
    sp.logger.info("Test households initialization methods.")

    # households = sp.Households()
    pop = sc.prettyobj()
    pop.households = []

    # test no households made
    sp.initialize_empty_households(pop)
    assert pop.n_households == 0, 'Check failed. households.n_households is not 0.'
    print('Check passed. Initially without any households information, households.n_households is 0.')

    homes_by_uids = [[1, 2, 3], [4], [7, 6, 5, 8, 9]]
    age_by_uid = {1: 88, 2: 45, 3: 47, 4: 38, 5: 12, 6: 19, 7: 55, 8: 58, 9: 99}

    pop.households = homes_by_uids
    pop.n_households = 2

    # households.households_array = homes_by_uids
    # households.n_households = 2
    assert pop.n_households != len(pop.households), 'Check failed. pop.n_households and len(pop.households_array) are not aligned.'
    print('Check passed. Initially households.n_households do not match len(households.households_array).')

    # households.initialize_n_households()
    # assert households.n_households == len(households.households_array), 'Check failed. households.n_households and len(households.households_array) do not match.'
    # print('Check passed. Now households.n_households and len(households.households_array).')

    pop.households = []
    sp.initialize_empty_households(pop, n_households=5)
    for i in range(pop.n_households):
        # assert isinstance(households.households_array[i], sp.Household) and households.get_household(i).get_hhid() is None, 'Check failed. households[i] is not a household object.'
        assert isinstance(pop.households[i], sp.Household) and pop.households[i]['hhid'] is None, 'Check failed. households[i] is not a household object.'
    print(f'Check passed. Initialized {pop.n_households} empty households.')

    # test that if there are not enough households when populating, we reinitialize that cover with the correct number
    # households.households_array = []
    pop.households = []
    sp.populate_households(pop, homes_by_uids, age_by_uid)
    assert len(pop.households) == len(homes_by_uids), 'Check failed.'
    print('Check passed.')


if __name__ == '__main__':

    test_cannot_change_attribute()
    pop = test_empty_household()
    test_make_household()
    test_add_household()
    test_households_basic()
    test_households_initialization()

    hhs = sp.Households()
    # print(hhs.keys())

