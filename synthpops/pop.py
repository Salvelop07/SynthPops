"""
This module provides the layer for communicating with the agent-based model Covasim.
"""

import os
import numpy as np
import sciris as sc
from .config import logger as log
from . import config as cfg
from . import sampling as spsamp
from . import base as spb
from . import data_distributions as spdata
from . import contact_networks as spcnx
from . import ltcfs as spltcf
from . import households as sphh
from . import schools as spsch
from . import workplaces as spw

part = 2 # CK: not sure what this is


class Pop(sc.prettyobj):

    def __init__(self, n=None, max_contacts=None, with_industry_code=False, with_facilities=False, use_default=False,
                    use_two_group_reduction=True, average_LTCF_degree=20, ltcf_staff_age_min=20, ltcf_staff_age_max=60,
                    with_school_types=False, school_enrollment_counts_available=False, school_mixing_type='random', average_class_size=20, inter_grade_mixing=0.1,
                    average_student_teacher_ratio=20, average_teacher_teacher_degree=3, teacher_age_min=25, teacher_age_max=75,
                    with_non_teaching_staff=False,
                    average_student_all_staff_ratio=15, average_additional_staff_degree=20, staff_age_min=20, staff_age_max=75,
                    rand_seed=None, country_location=None, state_location=None, location=None,
                    do_make=True):
        '''
        Make a full population network including both people (ages, sexes) and contacts using Seattle, Washington data.

        Args:
            n (int)                                 : The number of people to create.
            max_contacts (dict)                     : A dictionary for maximum number of contacts per layer: keys must be "W" (work).
            with_industry_code (bool)               : If True, assign industry codes for workplaces, currently only possible for cached files of populations in the US.
            with_facilities (bool)                  : If True, create long term care facilities, currently only available for locations in the US.
            use_default (bool)                      :  ?????
            use_two_group_reduction (bool)          : If True, create long term care facilities with reduced contacts across both groups.
            average_LTCF_degree (float)             : default average degree in long term care facilities.
            ltcf_staff_age_min (int)                : Long term care facility staff minimum age.
            ltcf_staff_age_max (int)                : Long term care facility staff maximum age.
            with_school_types (bool)                : If True, creates explicit school types.
            school_enrollment_counts_available (bool): ????
            school_mixing_type (str or dict)        : The mixing type for schools, 'random', 'age_clustered', or 'age_and_class_clustered' if string, and a dictionary of these by school type otherwise.
            average_class_size (float)              : The average classroom size.
            inter_grade_mixing (float)              : The average fraction of mixing between grades in the same school for clustered school mixing types.
            average_student_teacher_ratio (float)   : The average number of students per teacher.
            average_teacher_teacher_degree (float)  : The average number of contacts per teacher with other teachers.
            teacher_age_min (int)                   : The minimum age for teachers.
            teacher_age_max (int)                   : The maximum age for teachers.
            with_non_teaching_staff (bool)          : If True, includes non teaching staff.
            average_student_all_staff_ratio (float) : The average number of students per staff members at school (including both teachers and non teachers).
            average_additional_staff_degree (float) : The average number of contacts per additional non teaching staff in schools.
            staff_age_min (int)                     : The minimum age for non teaching staff.
            staff_age_max (int)                     : The maximum age for non teaching staff.
            rand_seed (int)                         : Start point random sequence is generated from.
            location                  : name of the location
            state_location (string)   : name of the state the location is in
            country_location (string) : name of the country the location is in
            sheet_name                : sheet name where data is located
            do_make (bool): whether to make the population

        Returns:
            network (dict): A dictionary of the full population with ages and connections.
        '''
        log.debug('Pop()')

        # Assign all the variables
        self.school_pars = sc.objdict()
        self.ltcf_pars = sc.objdict()
        self.n                               = n
        self.max_contacts                    = max_contacts
        self.with_industry_code              = with_industry_code
        self.rand_seed                       = rand_seed
        self.country_location                = country_location
        self.state_location                  = state_location
        self.location                        = location
        self.ltcf_pars.with_facilities                 = with_facilities
        self.ltcf_pars.use_two_group_reduction         = use_two_group_reduction
        self.ltcf_pars.average_LTCF_degree             = average_LTCF_degree
        self.ltcf_pars.ltcf_staff_age_min              = ltcf_staff_age_min
        self.ltcf_pars.ltcf_staff_age_max              = ltcf_staff_age_max
        self.ltcf_pars.use_default                      = use_default
        self.school_pars.with_school_types               = with_school_types
        self.school_pars.school_enrollment_counts_available = school_enrollment_counts_available
        self.school_pars.school_mixing_type              = school_mixing_type
        self.school_pars.average_class_size              = average_class_size
        self.school_pars.inter_grade_mixing              = inter_grade_mixing
        self.school_pars.average_student_teacher_ratio   = average_student_teacher_ratio
        self.school_pars.average_teacher_teacher_degree  = average_teacher_teacher_degree
        self.school_pars.teacher_age_min                 = teacher_age_min
        self.school_pars.teacher_age_max                 = teacher_age_max
        self.school_pars.with_non_teaching_staff         = with_non_teaching_staff
        self.school_pars.average_student_all_staff_ratio = average_student_all_staff_ratio
        self.school_pars.average_additional_staff_degree = average_additional_staff_degree
        self.school_pars.staff_age_min                   = staff_age_min
        self.school_pars.staff_age_max                   = staff_age_max


        # Handle more initialization
        if self.rand_seed is not None:
            spsamp.set_seed(self.rand_seed)

        default_max_contacts = {'W': 20}  # this can be anything but should be based on relevant average number of contacts for the population under study

        self.n = int(self.n)
        self.trimmed_size_dic = sc.mergedicts(default_max_contacts, self.max_contacts) # TODO: make names consistent

        # Handle data
        if self.country_location is None :
            self.country_location = cfg.default_country
            self.state_location = cfg.default_state
            self.location = cfg.default_location

        else:
            print(f"========== setting country location = {country_location}")
            cfg.set_location_defaults(country_location)
        # if country is specified, and state is not, we are doing a country population
        if self.state_location is None:
            self.location = None

        self.sheet_name = cfg.default_sheet_name
        self.datadir = cfg.datadir # Assume this has been reset...

        # Heavy lift 1: make the contacts and their connections
        log.debug('Generating a new population...')
        population = self.generate()

        # Change types
        for key, person in population.items():
            for layerkey in population[key]['contacts'].keys():
                population[key]['contacts'][layerkey] = list(population[key]['contacts'][layerkey])

        self.popdict = population
        log.debug('Pop(): done.')
        return


    def generate(self, verbose=False):
        ''' Actually generate the network '''

        log.debug('generate_microstructure_with_facilities()')

        print('TEMP: unpack variables')

        datadir = self.datadir
        location = self.location
        state_location = self.state_location
        country_location = self.country_location
        n = self.n
        sheet_name = self.sheet_name
        use_two_group_reduction = self.ltcf_pars.use_two_group_reduction
        average_LTCF_degree = self.ltcf_pars.average_LTCF_degree
        use_default = self.ltcf_pars.use_default
        ltcf_staff_age_min = self.ltcf_pars.ltcf_staff_age_min
        ltcf_staff_age_max = self.ltcf_pars.ltcf_staff_age_max
        school_enrollment_counts_available = self.school_pars.school_enrollment_counts_available
        with_school_types = self.school_pars.with_school_types
        school_mixing_type = self.school_pars.school_mixing_type
        average_class_size = self.school_pars.average_class_size
        inter_grade_mixing = self.school_pars.inter_grade_mixing
        average_student_teacher_ratio = self.school_pars.average_student_teacher_ratio
        average_teacher_teacher_degree = self.school_pars.average_teacher_teacher_degree
        teacher_age_min = self.school_pars.teacher_age_min
        teacher_age_max = self.school_pars.teacher_age_max
        average_student_all_staff_ratio = self.school_pars.average_student_all_staff_ratio
        average_additional_staff_degree = self.school_pars.average_additional_staff_degree
        staff_age_min = self.school_pars.staff_age_min
        staff_age_max = self.school_pars.staff_age_max
        trimmed_size_dic = self.trimmed_size_dic

        # Load the contact matrix
        contact_matrix_dic = spdata.get_contact_matrix_dic(datadir, sheet_name=sheet_name)

        # Generate LTCFs
        n_nonltcf, age_brackets_16, age_by_brackets_dic_16, ltcf_adjusted_age_distr, facilities = spltcf.generate_ltcfs(n, datadir, country_location, state_location, location, part, use_default)

        # Households
        household_size_distr = spdata.get_household_size_distr(datadir, location, state_location, country_location, use_default=use_default)
        hh_sizes = sphh.generate_household_sizes_from_fixed_pop_size(n_nonltcf, household_size_distr)
        hha_brackets = spdata.get_head_age_brackets(datadir, country_location=country_location, state_location=state_location, use_default=use_default)
        hha_by_size = spdata.get_head_age_by_size_distr(datadir, country_location=country_location, state_location=state_location, use_default=use_default, household_size_1_included=cfg.default_household_size_1_included)
        homes_dic, homes = spltcf.custom_generate_all_households(n_nonltcf, hh_sizes, hha_by_size, hha_brackets, age_brackets_16, age_by_brackets_dic_16, contact_matrix_dic, ltcf_adjusted_age_distr)

        # Households + facilities
        homes = facilities + homes
        homes_by_uids, age_by_uid_dic = sphh.assign_uids_by_homes(homes)  # include facilities to assign ids
        facilities_by_uids = homes_by_uids[0:len(facilities)]

        # Make a dictionary listing out uids of people by their age
        uids_by_age_dic = spb.get_ids_by_age_dic(age_by_uid_dic)

        # Generate school sizes
        school_sizes_count_by_brackets = spdata.get_school_size_distr_by_brackets(datadir, location=location, state_location=state_location, country_location=country_location, counts_available=school_enrollment_counts_available, use_default=use_default)
        school_size_brackets = spdata.get_school_size_brackets(datadir, location=location, state_location=state_location, country_location=country_location, use_default=use_default)

        # Figure out who's going to school as a student with enrollment rates (gets called inside sp.get_uids_in_school)
        uids_in_school, uids_in_school_by_age, ages_in_school_count = spsch.get_uids_in_school(datadir, n_nonltcf, location, state_location, country_location, age_by_uid_dic, homes_by_uids, use_default=use_default)  # this will call in school enrollment rates

        if with_school_types:

            school_size_distr_by_type = spsch.get_default_school_size_distr_by_type()
            school_size_brackets = spsch.get_default_school_size_distr_brackets()

            school_types_by_age = spsch.get_default_school_types_by_age()
            school_type_age_ranges = spsch.get_default_school_type_age_ranges()

            syn_schools, syn_school_uids, syn_school_types = spsch.send_students_to_school_with_school_types(school_size_distr_by_type, school_size_brackets, uids_in_school, uids_in_school_by_age,
                                                                                                             ages_in_school_count,
                                                                                                             school_types_by_age,
                                                                                                             school_type_age_ranges,
                                                                                                             verbose=verbose)
        else:
            # Get school sizes
            syn_school_sizes = spsch.generate_school_sizes(school_sizes_count_by_brackets, school_size_brackets, uids_in_school)
            # Assign students to school
            syn_schools, syn_school_uids, syn_school_types = spsch.send_students_to_school(syn_school_sizes, uids_in_school, uids_in_school_by_age, ages_in_school_count, age_brackets_16, age_by_brackets_dic_16, contact_matrix_dic, verbose)

        # Get employment rates
        employment_rates = spdata.get_employment_rates(datadir, location=location, state_location=state_location, country_location=country_location, use_default=use_default)

        # Find people who can be workers (removing everyone who is currently a student)
        potential_worker_uids, potential_worker_uids_by_age, potential_worker_ages_left_count = spw.get_uids_potential_workers(syn_school_uids, employment_rates, age_by_uid_dic)
        workers_by_age_to_assign_count = spw.get_workers_by_age_to_assign(employment_rates, potential_worker_ages_left_count, uids_by_age_dic)

        # Get facility staff
        facilities_staff_uids, potential_worker_uids, workers_by_age_to_assign_count = spltcf.assign_facility_staff(datadir, location, state_location, country_location, ltcf_staff_age_min, ltcf_staff_age_max, facilities, workers_by_age_to_assign_count, potential_worker_uids_by_age, potential_worker_uids, facilities_by_uids, age_by_uid_dic)

        # Assign teachers and update school lists
        syn_teachers, syn_teacher_uids, potential_worker_uids, potential_worker_uids_by_age, workers_by_age_to_assign_count = spsch.assign_teachers_to_schools(syn_schools, syn_school_uids, employment_rates, workers_by_age_to_assign_count, potential_worker_uids, potential_worker_uids_by_age, potential_worker_ages_left_count,
                                                                                                                                                               average_student_teacher_ratio=average_student_teacher_ratio, teacher_age_min=teacher_age_min, teacher_age_max=teacher_age_max, verbose=verbose)
        syn_non_teaching_staff_uids, potential_worker_uids, potential_worker_uids_by_age, workers_by_age_to_assign_count = spsch.assign_additional_staff_to_schools(syn_school_uids, syn_teacher_uids, workers_by_age_to_assign_count, potential_worker_uids, potential_worker_uids_by_age, potential_worker_ages_left_count,
                                                                                                                                                                    average_student_teacher_ratio=average_student_teacher_ratio, average_student_all_staff_ratio=average_student_all_staff_ratio, staff_age_min=staff_age_min, staff_age_max=staff_age_max, verbose=verbose)

        # Generate non-school workplace sizes needed to send everyone to work
        workplace_size_brackets = spdata.get_workplace_size_brackets(datadir, state_location=state_location, country_location=country_location, use_default=use_default)
        workplace_size_distr_by_brackets = spdata.get_workplace_size_distr_by_brackets(datadir, state_location=state_location, country_location=country_location, use_default=use_default)
        workplace_sizes = spw.generate_workplace_sizes(workplace_size_distr_by_brackets, workplace_size_brackets, workers_by_age_to_assign_count)

        # Assign all workers who are not staff at schools to workplaces
        syn_workplaces, syn_workplace_uids, potential_worker_uids, potential_worker_uids_by_age, workers_by_age_to_assign_count = spw.assign_rest_of_workers(workplace_sizes, potential_worker_uids, potential_worker_uids_by_age, workers_by_age_to_assign_count, age_by_uid_dic, age_brackets_16, age_by_brackets_dic_16, contact_matrix_dic, verbose=verbose)

        # remove facilities from homes to write households as a separate file
        homes_by_uids = homes_by_uids[len(facilities_by_uids):]

        # Generate the population
        population = spcnx.make_contacts_from_microstructure_objects(age_by_uid_dic=age_by_uid_dic,
                                                                 homes_by_uids=homes_by_uids,
                                                                 schools_by_uids=syn_school_uids,
                                                                 teachers_by_uids=syn_teacher_uids,
                                                                 non_teaching_staff_uids=syn_non_teaching_staff_uids,
                                                                 workplaces_by_uids=syn_workplace_uids,
                                                                 facilities_by_uids=facilities_by_uids,
                                                                 facilities_staff_uids=facilities_staff_uids,
                                                                 use_two_group_reduction=use_two_group_reduction,
                                                                 average_LTCF_degree=average_LTCF_degree,
                                                                 with_school_types=with_school_types,
                                                                 school_mixing_type=school_mixing_type,
                                                                 average_class_size=average_class_size,
                                                                 inter_grade_mixing=inter_grade_mixing,
                                                                 average_student_teacher_ratio=average_student_teacher_ratio,
                                                                 average_teacher_teacher_degree=average_teacher_teacher_degree,
                                                                 average_student_all_staff_ratio=average_student_all_staff_ratio,
                                                                 average_additional_staff_degree=average_additional_staff_degree,
                                                                 trimmed_size_dic=trimmed_size_dic)

        return population


    def to_dict(self):
        ''' Export to a dictionary '''
        return sc.dcp(self.popdict)
