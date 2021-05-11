"""Test Zimbabwe location works and plot the demographics and contact networks."""
import sciris as sc
import synthpops as sp
import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
import settings
import pytest


default_nbrackets = sp.settings.nbrackets

pars = sc.objdict(
    n                = settings.pop_sizes.large * 10,
    rand_seed        = 0,

    household_method = 'fixed_ages',
    smooth_ages      = 1,

    country_location = 'Zimbabwe',
    sheet_name       = 'Zimbabwe',
    use_default      = True,
    with_school_types = 1,
)

if __name__ == '__main__':
    sp.set_location_defaults(country_location="Senegal")
    pop = sp.Pop(**pars)
    print(pop.summarize())
    pop.plot_ages()
    pop.plot_household_sizes()
    pop.plot_enrollment_rates_by_age()
    pop.plot_contacts(layer='H', density_or_frequency='density', logcolors_flag=0, title_prefix="Zimbabwe Age Mixing")
    pop.plot_school_sizes(with_school_types=1)
    pop.plot_employment_rates_by_age()
    pop.plot_workplace_sizes()
    sp.set_location_defaults()
    plt.show()
