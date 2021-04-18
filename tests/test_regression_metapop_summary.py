"""
Test advanced regression method
"""
import numpy as np
import sciris as sc
import synthpops as sp
import covasim as cv
import matplotlib as mplt
import matplotlib.pyplot as plt
import seaborn as sns


pars = sc.objdict(
    n                       = 5e3,
    rand_seed               = 123,
    smooth_ages             = 1,

    household_method = 'fixed_ages',

    with_facilities         = 1,
    with_non_teaching_staff = 1,
    with_school_types       = 1,

    school_mixing_type      = {'pk': 'random',
                          'es': 'random',
                          'ms': 'random',
                          'hs': 'random',
                          'uv': 'random'
                          },

)


def test_count_layer_degree():

    pop = sp.Pop(**pars)

    layer = 'S'
    ages = None
    uids = None
    # uids = [0, 1]
    # ages = [95, 89, 90, 91]
    # ages = np.arange(5, 25)
    degree_df = sp.count_layer_degree(pop, layer, ages, uids)
    # print(degree_df.loc[degree_df['age'] == 20])

    # stats = sp.compute_layer_degree_statistics(pop, degree_df=degree_df)
    cmap = sns.cubehelix_palette(light=1, as_cmap=True)
    # cmap = mplt.cm.get_cmap('mako_r')

    # g = sns.jointplot(x="age", y="degree", data=degree_df, cmap=cmap, alpha=0.75,
    #                   xlim=[0, 101], kind='kde', shade=True, thresh=0.01,
    #                   color=cmap(0.9), ylim=[0, 6],
    #                   space=0).plot_marginals(sns.kdeplot, color=cmap(0.75),
    #                                           shade=True, alpha=.5, legend=False)

    kwargs = sc.objdict()
    # kwargs.xlim = [3, 70]
    kwargs.figname = 'hex_degree'
    kwargs.do_save = 1

    # kind = 'kde'
    kind = 'hist'
    # kind = 'reg'
    # kind = 'hex'

    # g = sp.plotting.plot_degree_by_age(pop, layer=layer, degree_df=degree_df, kind=kind, **kwargs)

    # ax = sp.plotting.plot_degree_by_age_2(pop, layer=layer, degree_df=degree_df, **kwargs)
    # fig, axes = plt.subplots(1, 3, figsize=(12, 3), sharex=True, sharey=True)
    # fig.subplots_adjust(left=0.06, right=0.97, bottom=0.15)

    pars2 = sc.dcp(pars)
    pars2['rand_seed'] = 0
    # alpha = 0.95
    # thresh = 0.001

    pop2 = sp.Pop(**pars2)
    # degree_df2 = sp.count_layer_degree(pop2, layer, ages, uids)
    # cmap2 = sns.cubehelix_palette(rot=0.3, light=1, as_cmap=True)

    pars3 = sc.dcp(pars)
    pars3['rand_seed'] = 1

    pop3 = sp.Pop(**pars3)
    # degree_df3 = sp.count_layer_degree(pop3, layer, ages, uids)
    # cmap3 = sns.cubehelix_palette(rot=0.2, light=1, as_cmap=True)

    # # g.plot_joint(sns.kdeplot, data=degree_df2, cmap=cmap2, alpha=0.75, xlim=[0, 101], kind='kde', shade=True, thresh=0.01, color=cmap2(0.9), ylim=[0, 6], space=0).plot_marginals(sns.kdeplot, color=cmap2(0.75), shade=True, alpha=0.5, legend=False)

    pars4 = sc.dcp(pars)
    pars4['rand_seed'] = 2
    pop4 = sp.Pop(**pars4)

    pars5 = sc.dcp(pars)
    pars5['rand_seed'] = 3
    pop5 = sp.Pop(**pars5)

    pars6 = sc.dcp(pars)
    pars6['rand_seed'] = 4
    pop6 = sp.Pop(**pars6)

    fig, axes = sp.plotting.plot_multi_degree_by_age([pop, pop2, pop3, pop4, pop5, pop6], layer='S', ages=ages, kind=kind, **kwargs)

    plt.show()

    return pop



def test_multiple_degree_histplots()







if __name__ == '__main__':

    test_count_layer_degree()
