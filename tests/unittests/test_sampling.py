'''
Test sampling methods.
'''

import sciris as sc
import synthpops as sp
import numpy as np
import pytest
import scipy


def test_fast_choice(do_plot=False, sigma=5):
    sc.heading('Testing fast_choice()...')

    # Settings
    n = 10000
    weights = np.array([1,2,4,2,1])
    nwts = len(weights)
    vals = np.arange(nwts)
    expected = np.sum(vals*weights)/np.sum(weights)

    # Calculate
    samples = np.zeros(n)
    for i in range(n):
        samples[i] = sp.fast_choice(weights)

    if do_plot:
        import pylab as pl
        pl.hist(samples, bins=np.arange(nwts+1), width=0.8)
        norm = n/(sum(weights))
        pl.scatter(vals+0.4, weights*norm, s=100, c='k', marker='x', zorder=10, label='Expected')
        pl.legend()
        pl.xlabel('Choice')
        pl.ylabel('Number of samples')
        pl.show()

    # Check that it's close
    assert np.isclose(samples.mean(), expected, atol=sigma/np.sqrt(n))

    return samples


def test_check_dist_poisson():
    sc.heading('Testing test_check_dist_poisson() (statistical tests for a discrete distribution)...')

    # Poisson tests
    n              = 100 # Number of samples
    expected       = 10 # Target value
    actual_valid   = 12 # Close to target given the number of samples
    actual_invalid = 20 # Far from target
    invalid_data = np.random.rand(n) + expected

    print('↓ Should print some warnings')
    sp.check_poisson(actual=actual_valid, expected=expected, die=True) # Should pass
    sp.check_poisson(actual=actual_invalid, expected=expected, verbose=False) # Shouldn't pass, but not die
    sp.check_poisson(actual=actual_valid, expected=expected, check='median') # Should pass checking against median

    sp.check_poisson(actual=np.zeros(100), expected=0, verbose=True, check='mean')
    stats = sp.check_poisson(actual=invalid_data, expected=expected, label='Example', verbose=True, stats=True) # Shouldn't pass, print warning

    with pytest.raises(ValueError):
        sp.check_poisson(actual=actual_invalid, expected=expected, die=True)
    with pytest.raises(ValueError):
        sp.check_poisson(actual=actual_valid, expected=expected, alpha=1.0, die=True)

    return stats


def test_check_dist_normal():
    sc.heading('Testing test_check_dist_normal() (statistical tests for a continuous distribution)...')
    # Normal tests
    n             = 100
    expected      = 5
    invalid       = 15
    std           = 3
    valid_ndata   = np.random.randn(n)*std + expected
    invalid_ndata = np.random.randn(n)*std + invalid
    sp.check_normal(actual=valid_ndata, expected=expected, die=True)
    with pytest.raises(ValueError):
        sp.check_normal(actual=invalid_ndata, expected=expected, die=True)


def test_check_dist_binom():
    sc.heading('Testing test_check_dist_binom() (statistical tests for a discrete distribution)...')
    # Binomial tests
    n = 300
    p = 0.06
    size = 300
    expected = (n, p)  # n, p
    actual = scipy.stats.binom.rvs(n, p, size=size)
    sp.check_dist(actual=actual, expected=expected, dist='binom', check='dist', verbose=True)


def test_other_distributions():
    sc.heading('Testing test_other_distributions()...')
    # Other tests
    sp.check_dist(actual=5.5, expected=(1, 5), dist='lognorm', die=True)
    with pytest.raises(NotImplementedError):
        sp.check_dist(actual=1, expected=1, dist='not a distribution')


if __name__ == '__main__':

    T = sc.tic()

    # choices = test_fast_choice()
    # stats = test_check_dist_poisson()
    # test_check_dist_normal()
    test_check_dist_binom()
    # test_other_distributions()

    sc.toc(T)
    print('Done.')
