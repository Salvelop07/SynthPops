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

mplt.rcParams['font.family'] = 'Roboto Condensed'
mplt.rcParams['font.size'] = 7


# parameters to generate a test population
pars = dict(
    n                               = 20e3,
    rand_seed                       = 123,
    max_contacts                    = None,

    country_location                = 'usa',
    state_location                  = 'Washington',
    location                        = 'seattle_metro',
    use_default                     = True,

    with_industry_code              = 0,
    with_facilities                 = 1,
    with_non_teaching_staff         = 1,
    use_two_group_reduction         = 1,
    with_school_types               = 1,

    average_LTCF_degree             = 20,
    ltcf_staff_age_min              = 20,
    ltcf_staff_age_max              = 60,

    school_mixing_type              = {'pk': 'age_and_class_clustered', 'es': 'age_and_class_clustered', 'ms': 'age_and_class_clustered', 'hs': 'random', 'uv': 'random'},  # you should know what school types you're working with
    average_class_size              = 20,
    inter_grade_mixing              = 0.1,
    teacher_age_min                 = 25,
    teacher_age_max                 = 75,
    staff_age_min                   = 20,
    staff_age_max                   = 75,

    average_student_teacher_ratio   = 20,
    average_teacher_teacher_degree  = 3,
    average_student_all_staff_ratio = 11,
    average_additional_staff_degree = 20,
)


def test_school_types_created():
    """
    Test that unique school types are created.

    Returns:
        A list of the school types expected for the specified location.
    """
    sp.logger.info(f"Test that unique school types are created for each school.\nRun this first to see what school types you are working with.")

    test_pars = sc.dcp(pars)
    test_pars['n'] = 20e3
    pop = sp.make_population(**test_pars)
    if pars['with_school_types']:
        expected_school_size_distr = sp.get_school_size_distr_by_type(sp.datadir, location=pars['location'], state_location=pars['state_location'], country_location=pars['country_location'], use_default=pars['use_default'])
        expected_school_types = sorted(expected_school_size_distr.keys())

    else:
        expected_school_types = [None]

    schools_by_type = dict()
    for i, person in pop.items():
        if person['scid'] is not None:
            schools_by_type.setdefault(person['scid'], set())
            schools_by_type[person['scid']].add(person['sc_type'])

    for s, school_type in schools_by_type.items():
        assert len(school_type) == 1, f'Check failed. School {s} is listed as having more than one type.'
        schools_by_type[s] = list(school_type)[0]

    gen_school_types = sorted(set(schools_by_type.values()))
    assert gen_school_types == expected_school_types, f"Check failed. generated types: {gen_school_types}, expected: {expected_school_types}"

    print(f"School types generated for {test_pars['location']}: {set(schools_by_type.values())}")

    return list(set(schools_by_type.values()))


def plot_school_sizes_by_type(pop, pars, do_show=False):
    """
    Plot the school size distribution by type compared with the expected data.
    """
    sp.logger.info(f"Plotting to show that school sizes are generated by school type when the parameter 'with_school_types' is set to True.")

    if pars['with_school_types']:
        expected_school_size_distr = sp.get_school_size_distr_by_type(sp.datadir, location=pars['location'], state_location=pars['state_location'], country_location=pars['country_location'], use_default=pars['use_default'])
        school_size_brackets = sp.get_school_size_brackets(sp.datadir, location=pars['location'], state_location=pars['state_location'], country_location=pars['country_location'])  # for right now the size distribution for all school types will use the same brackets or bins
    else:
        expected_school_size_distr = {None: sp.get_school_size_distr_by_brackets(sp.datadir, location=pars['location'], state_location=pars['state_location'], country_location=pars['country_location'], use_default=pars['use_default'])}
        school_size_brackets = sp.get_school_size_brackets(sp.datadir, location=pars['location'], state_location=pars['state_location'], country_location=pars['country_location'])

    bins = [school_size_brackets[0][0]] + [school_size_brackets[b][-1] + 1 for b in school_size_brackets]

    schools = dict()
    enrollment_by_school_type = dict()
    gen_school_size_distr = dict()

    for i, person in pop.items():
        if person['scid'] is not None and person['sc_student']:
            schools.setdefault(person['scid'], dict())
            schools[person['scid']]['sc_type'] = person['sc_type']
            schools[person['scid']].setdefault('enrolled', 0)
            schools[person['scid']]['enrolled'] += 1

    for i, school in schools.items():
        enrollment_by_school_type.setdefault(school['sc_type'], [])
        enrollment_by_school_type[school['sc_type']].append(school['enrolled'])

    for sc_type in enrollment_by_school_type:
        sizes = enrollment_by_school_type[sc_type]
        hist, bins = np.histogram(sizes, bins=bins, density=0)
        gen_school_size_distr[sc_type] = {i: hist[i] / sum(hist) for i in school_size_brackets}

    gen_school_size_distr = sc.objdict(gen_school_size_distr)

    width = 6
    height = 3 * len(gen_school_size_distr)
    hspace = 0.4

    cmap = cmr.get_sub_cmap('cmo.curl', 0.12, 1)
    fig, ax = plt.subplots(len(gen_school_size_distr), 1, figsize=(width, height), tight_layout=True)
    plt.subplots_adjust(hspace=hspace)
    if len(gen_school_size_distr) == 1:
        ax = [ax]

    bin_labels = [f"{school_size_brackets[b][0]}-{school_size_brackets[b][-1]}" for b in school_size_brackets]

    sorted_school_types = sorted(gen_school_size_distr.keys())

    for ns, school_type in enumerate(sorted_school_types):
        x = np.arange(len(school_size_brackets))

        c = ns / len(gen_school_size_distr)
        c2 = min(c + 0.1, 1)

        sorted_bins = sorted(expected_school_size_distr[school_type].keys())

        ax[ns].bar(x, [expected_school_size_distr[school_type][b] for b in sorted_bins], color=cmap(c), edgecolor='white', label='Expected', zorder=0)
        ax[ns].plot(x, [gen_school_size_distr[school_type][b] for b in sorted_bins], color=cmap(c2), ls='--',
                    marker='o', markerfacecolor=cmap(c2), markeredgecolor='white', markeredgewidth=.5, markersize=5, label='Simulated', zorder=1)

        leg = ax[ns].legend(loc=1)
        leg.draw_frame(False)
        ax[ns].set_xticks(x)
        ax[ns].set_xticklabels(bin_labels, rotation=25)
        ax[ns].set_xlim(0, x[-1])
        ax[ns].set_ylim(0, 1)
        if school_type is None:
            title = "without school types defined"
        else:
            title = f"{school_type}"

        if ns == 0:
            if pars['location'] is not None:
                location_text = f"{pars['location'].replace('_', ' ').title()}"
            else:
                location_text = f"{sp.config.default_location.replace('_', ' ').title()} Default Sizes"

            ax[ns].text(0., 1.1, location_text, horizontalalignment='left', fontsize=10)

        ax[ns].set_title(title, fontsize=10)

    ax[ns].set_xlabel('School size')

    if do_show:
        plt.show()

    return fig, ax, sorted_school_types


@pytest.mark.parametrize("pars", [pars])
def test_school_sizes_by_type(pars, do_show=False):
    """
    Visually show how the school size distribution generated compares to the
    data for the location being simulated.

    Notes:
        The larger the population size, the better the generated school size
        distributions by school type can match the expected data. If generated
        populations are too small, larger schools will be missed and in
        general there won't be enough schools generated to apply statistical
        tests.
    """
    sp.logger.info("Creating schools by school type and a visual comparison of how they match to data.")
    pop = sp.make_population(**pars)
    fig, ax, school_types = plot_school_sizes_by_type(pop, pars, do_show=do_show)

    return pop, fig, ax, school_types


@pytest.mark.parametrize("pars", [pars])
def test_separate_school_types_for_seattle_metro(pars, do_show=False):
    """
    Notes:
        By default, when no location is given and use_default is set to True,
        data pulled in will be for seattle metro and school type data will
        default to previous seattle metro data with pre-k and elementary kept
        separate.
    """
    sp.logger.info("Creating schools where pre-k and elementary schools are separate.")
    test_pars = sc.dcp(pars)
    test_pars['location'] = None  # seattle_metro results with school size distribution the same for all types
    pop = sp.make_population(**pars)
    fig, ax, school_types = plot_school_sizes_by_type(pop, test_pars, do_show=do_show)

    assert ('pk' in school_types) and ('es' in school_types), 'Check failed. pk and es school type are not separately created.'
    print('Check passed.')

    return pop, fig, ax, school_types


def test_without_school_types(do_show=False):
    """
    Test that without school types, all schools are put together in one group.
    """
    sp.logger.info("Creating schools where with_school_types is False.")
    test_pars = sc.dcp(pars)
    test_pars['with_school_types'] = None
    pop = sp.make_population(**test_pars)
    fig, ax, school_types = plot_school_sizes_by_type(pop, test_pars, do_show=do_show)
    return pop, fig, ax, school_types


if __name__ == '__main__':

    # run as main to see the code and figures in action!

    sc.tic()

    school_types = test_school_types_created()
    pop, fig, ax, school_types = test_school_sizes_by_type(pars, do_show=True)
    pop2, fig2, ax2, school_types2 = test_separate_school_types_for_seattle_metro(pars, do_show=True)
    pop3, fig3, ax3, school_types3 = test_without_school_types(do_show=True)

    plt.show()
    sc.toc()
