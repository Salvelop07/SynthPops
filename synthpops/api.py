import sciris as sc
import synthpops as sp

# Put this here so it's accessible as sp.api.choices
popsize_choices = [5000,
                   10000,
                   20000,
                   50000,
                   100000,
                   122000,
                ]


def make_network(n=None, max_contacts=None):
    '''
    Make a full network including both people (ages, sexes)

    Args:
        n (int): number of people to create
        max_contacts (dict): dictionary for maximum number of contacts per layer: keys must be 'S' (school) and/or 'W' (work)

    Returns:
        network (dict): a dictionary of the full population with ages and connections

    '''

    default_n = 20000
    default_max_contacts = {'S':20, 'W':10}

    if n is None: n = default_n
    n = int(n)
    if n not in popsize_choices:
        choicestr = ', '.join([str(choice) for choice in popsize_choices])
        errormsg = f'Number of people must be one of {choicestr}, not {n}'
        raise ValueError(errormsg)

    max_contacts = sc.mergedicts(default_max_contacts, max_contacts)

    state_location = 'Washington'
    location = 'seattle_metro'

    options_args = {'use_microstructure': True}
    network_distr_args = {'Npop': int(n)}

    # Heavy lift 1: make the contacts and their connections
    network = sp.make_contacts(state_location = state_location,location = location, options_args = options_args, network_distr_args = network_distr_args)

    # Semi-heavy-lift 2: trim them to the desired numbers
    network = sp.trim_contacts(network, trimmed_size_dic=max_contacts, use_clusters=False)

    return network
