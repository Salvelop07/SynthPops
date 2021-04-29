"""Testing the different school mixing types."""
import sciris as sc
import synthpops as sp
import numpy as np
import networkx as nx
import settings
import pytest

# parameters to generate a test population
pars = sc.objdict(
        n                               = settings.pop_sizes.medium,
        rand_seed                       = 123,

        with_facilities                 = 1,
        with_non_teaching_staff         = 1,
        with_school_types               = 1,
        average_student_teacher_ratio   = 20,

        school_mixing_type              = 'random',
)


@pytest.mark.parametrize("average_class_size", [12, 20, 30, 50, 100])
def test_random_schools(average_class_size):
    sp.logger.info("Test random school networks.")
    test_pars = sc.dcp(pars)
    test_pars['average_class_size'] = average_class_size
    pop = sp.Pop(**test_pars)

    G = nx.Graph()

    for i, person in pop.popdict.items():
        if person['scid'] is not None:

            # only for students and teachers
            if (person['sc_student'] == 1) | (person['sc_teacher'] == 1):
                contacts = person['contacts']['S']

                # we only expect this to pass for edges among students and teachers, non teaching staff are added after
                contacts = [c for c in contacts if (pop.popdict[c]['sc_student'] == 1) | (pop.popdict[c]['sc_teacher'] == 1)]
                edges = [(i, c) for c in contacts]
                G.add_edges_from(edges)

    g = [G.subgraph(c) for c in nx.connected_components(G)]  # split into each disconnected school

    for c in range(len(g)):

        expected_density = min(pop.school_pars.average_class_size / len(g[c].nodes()), 1)
        density = nx.density(g[c])
        clustering = nx.transitivity(g[c])

        lowerbound = 0.9
        upperbound = 1.1
        # check overall density of edges is as expected
        assert expected_density * lowerbound < density < expected_density * upperbound, 'Check failed on random graph densities.'

        # check that the distribution of edges is random and clustered as expected for a random graph
        assert expected_density * lowerbound < clustering < expected_density * upperbound, f'Check failed on random graph clustering. {clustering} {density} {expected_density} {np.mean([g[c].degree(n) for n in g[c].nodes()])} {len(g[c].nodes())}'
        print(f"Check passed. School {c} with random mixing has clustering {clustering:.3f} and density {density:.3f} close to expected value {expected_density:.3f}. {len(g[c].nodes())}")


if __name__ == '__main__':
    pytest.main(['-vs', __file__])
