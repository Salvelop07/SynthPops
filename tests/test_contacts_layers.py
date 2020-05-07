import synthpops as sp
import unittest
import random
import json
import os
from copy import deepcopy

"""
An example of how to load synthetic populations with microstructure (households, schools, and workplaces)
Populations have demographics (age, sex) from data.
Not an exhaustive list of what synthpops can do - please take a look through the code base for the many possibilities.
"""
#region pre-test setup
datadir = sp.datadir  # point datadir where your data folder lives

# location information - currently we only support the Seattle Metro area in full, however other locations can be supported with this framework at a later date
location = 'seattle_metro'
state_location = 'Washington'
country_location = 'usa'
sheet_name = 'United States of America'
level = 'county'

n = 20000
verbose = True
plot = True

# loads population with microstructure and age demographics that approximate those of the location selected
# files located in:
#    datadir/demographics/contact_matrices_152_countries/state_location/

# load population into a dictionary of individuals who know who their contacts are
options_args = {'use_microstructure': True}
network_distr_args = {'Npop': n}
contacts = sp.make_contacts(location=location, state_location=state_location,
                            country_location=country_location, options_args=options_args,
                            network_distr_args=network_distr_args)

# not all school and workplace contacts are going to be close contacts so create 'closer' contacts for these settings
# close_contacts_number = {'S': 20, 'W': 20}
# close_contacts_number = {'S': 10, 'W': 10}
# CONTACTS = sp.trim_contacts(contacts, trimmed_size_dic=close_contacts_number)
CONTACTS = contacts
#endregion


class SynthpopsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contacts = CONTACTS
        self.is_debugging = False
        pass

    def tearDown(self) -> None:
        pass

    def test_contacts_are_bidirectional(self):
        num_people = 5
        checked_people = []
        last_index_checked = 0
        self.is_debugging = True
        while len(checked_people) < num_people:
            popdict = deepcopy(self.contacts)

            uids = popdict.keys()
            uid_list = list(uids)
            my_uid = None
            while not my_uid:
                potential_uid = uid_list[last_index_checked]
                if potential_uid not in checked_people:
                    my_uid = potential_uid
                    checked_people.append(my_uid)
                    pass
                else:
                    last_index_checked += 1
                pass

            first_person = popdict[my_uid]

            person_json = {'uid': my_uid}
            for k in ['age', 'sex', 'loc']:
                person_json[k] = first_person[k]
                pass
            contact_keys = first_person['contacts'].keys()

            person_json['contacts'] = {}
            for k in list(contact_keys):
                these_contacts = first_person['contacts'][k]
                uids = []
                for uid in these_contacts:
                    uids.append(uid)
                    pass
                person_json['contacts'][k] = uids
                pass

            if self.is_debugging:
                person_filename = f"DEBUG_popdict_person_{my_uid}.json"
                print(f"TEST: {my_uid}")
                if os.path.isfile(person_filename):
                    os.unlink(person_filename)
                    pass
                with open(person_filename,"w") as outfile:
                    json.dump(person_json, outfile, indent=4, sort_keys=True)
                    pass
                pass

            # Now check that each person in each network has me in their network
            for k in person_json['contacts']:
                expected_uids = person_json['contacts'][k]
                for uid in expected_uids:
                    friend = popdict[uid]
                    friend_contact_group = list(friend['contacts'][k])
                    self.assertIn(my_uid, friend_contact_group)
                    pass

    def test_contact_layers_are_same_for_all_members(self):
        # Get four persons, one each with a home, work, school, and community layer
        popdict = deepcopy(self.contacts)
        representative_people = {
            "H": None,
            "S": None,
            "W": None
        }
        # TODO: add "C": None to above dictionary if that is ever supported here.
        try_this_next = 0
        indexes = list(popdict.keys())
        for k in representative_people.keys():
            while not representative_people[k]:
                temp_person = popdict[indexes[try_this_next]]
                if try_this_next % 1000 == 0:
                    print(f"At index {try_this_next} of {len(popdict)}")
                if len(temp_person['contacts'][k]) > 0:
                    print(f"Found my {k}\n")
                    representative_people[k] = indexes[try_this_next]
                elif try_this_next < 1000:
                    try_this_next += 1
                else:  # We went through 1000 people and are missing one
                    break

        if self.is_debugging:
            print(f"Representative people: {representative_people}")
            print(f"Try this next: {try_this_next}")
            pass

        for k in representative_people:
            if representative_people[k]:
                layer_friends = list(popdict[representative_people[k]]['contacts'][k])
                other_layer_person = popdict[layer_friends[0]]
                layer_friends.remove(layer_friends[0]) # add that person's uid back
                other_layer_friends = list(other_layer_person['contacts'][k])
                other_layer_friends.remove(representative_people[k])
                self.assertEqual(sorted(layer_friends), sorted(other_layer_friends),
                                 msg="The lists of uids should be identical")
            else:
                print(f"This is totally embarassing, no one found with layer {k}\n")


        # For each person, extract that layer into a list, and add that person's uid
        # Loop through each person in the list and
        #    Get the set of people in that same layer, append that person's uid
        #        Sort the list and compare to the top-level list, should be the same
        pass

    def test_trimmed_contacts_are_bidirectional(self):
        num_people = 5
        checked_people = []
        last_index_checked = 0
        close_contacts_numbers = {'S': 10, 'W': 10}
        self.is_debugging = True

        my_contacts = sp.make_contacts(location=location, state_location=state_location,
                                      country_location=country_location, options_args=options_args,
                                      network_distr_args=network_distr_args)
        my_trim_contacts = sp.trim_contacts(my_contacts, trimmed_size_dic=close_contacts_numbers)

        popdict = my_trim_contacts

        uids = popdict.keys()
        uid_list = list(uids)

        while len(checked_people) < num_people:
            my_uid = None
            while not my_uid:
                potential_uid = uid_list[last_index_checked]
                if potential_uid not in checked_people:
                    my_uid = potential_uid
                    checked_people.append(my_uid)
                    pass
                else:
                    last_index_checked += 1
                pass

            first_person = popdict[my_uid]

            person_json = {'uid': my_uid}
            for k in ['age', 'sex', 'loc']:
                person_json[k] = first_person[k]
                pass
            contact_keys = first_person['contacts'].keys()

            person_json['contacts'] = {}
            for k in list(contact_keys):
                these_contacts = first_person['contacts'][k]
                uids = []
                for uid in these_contacts:
                    uids.append(uid)
                    pass
                person_json['contacts'][k] = uids
                pass

            if self.is_debugging:
                person_filename = f"DEBUG_popdict_person_{my_uid}.json"
                print(f"TEST: {my_uid}")
                if os.path.isfile(person_filename):
                    os.unlink(person_filename)
                    pass
                with open(person_filename,"w") as outfile:
                    json.dump(person_json, outfile, indent=4, sort_keys=True)
                    pass
                pass

            # Now check that each person in each network has me in their network
            for k in person_json['contacts']:
                expected_uids = person_json['contacts'][k]
                for uid in expected_uids:
                    friend = popdict[uid]
                    friend_contact_group = list(friend['contacts'][k])
                    self.assertIn(my_uid, friend_contact_group)
                    pass
        pass




