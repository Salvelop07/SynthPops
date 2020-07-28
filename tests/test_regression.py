"""
Test regressions with fixed seed
expected files are in the "expected" folder
the filename has pattern pop_{n}_seed{seed}.json
"""

import unittest
import os
import shutil
import sys
import tempfile
import sciris as sc
import synthpops as sp
import inspect
import numpy as np
from fpdf import FPDF
from scipy.spatial import distance
from examples import plot_age_mixing_matrices

class TestRegression(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.resultdir = tempfile.TemporaryDirectory().name
        cls.figDir = os.path.join(cls.resultdir, "figs")
        cls.configDir = os.path.join(cls.resultdir, "configs")
        cls.pdfDir = os.path.join(os.path.dirname(__file__), "report")
        os.makedirs(cls.pdfDir, exist_ok=True)
        os.makedirs(cls.figDir, exist_ok=True)
        os.makedirs(cls.configDir, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.resultdir, ignore_errors=True)

    def test_regression_make_population(self):
        #set params, make sure name is identical to param names
        n = 10001
        rand_seed = 1001
        max_contacts = None
        with_industry_code = False
        with_facilities = False
        use_two_group_reduction = False
        average_LTCF_degree = 20
        generate = True
        #
        test_prefix = sys._getframe().f_code.co_name
        filename = os.path.join(self.resultdir,f'pop_{n}_seed{rand_seed}.json')
        actual_vals = locals()
        pop = self.runpop(filename=filename, actual_vals=actual_vals, testprefix=test_prefix)
        # if default sort order is not concerned:
        # pop = dict(sorted(pop.items(), key=lambda x: x[0]))

        sc.savejson(filename, pop, indent=2)
        self.check_result(actual_file=filename, prefix=test_prefix)
        self.generate_reports()

    def runpop(self, filename, actual_vals, testprefix = "test"):
        # if default sort order is not concerned:
        # pop = dict(sorted(pop.items(), key=lambda x: x[0]))
        params = {}
        args = inspect.getfullargspec(sp.make_population).args
        defaults = inspect.getfullargspec(sp.make_population).defaults
        for i in range(0, len(args)):
            params[args[i]] = defaults[i]
        for name in actual_vals:
            if name in params.keys():
                params[name] = actual_vals[name]
        with open(os.path.join(self.configDir, f"{testprefix}.txt"), mode="w") as cf:
            for key, value in params.items():
                cf.writelines(str(key) + ':' + str(value) + "\n")

        pop = sp.make_population(**params)
        return pop

    def check_result(self, actual_file, expected_file = None, prefix="test"):
        if not os.path.isfile(actual_file):
            raise FileNotFoundError(actual_file)
        if expected_file is None:
            expected_file = os.path.join(os.path.join(os.path.dirname(__file__), 'expected'), os.path.basename(actual_file))
        if not os.path.isfile(expected_file):
            raise FileNotFoundError(expected_file)
        expected = self.cast_uid_toINT(sc.loadjson(expected_file))
        actual = self.cast_uid_toINT(sc.loadjson(actual_file))
        #self.check_similarity(actual, expected)

        # generate the figures for comparison
        for code in ['H', 'W', 'S']:
            for type in ['density', 'frequency']:
                fig = plot_age_mixing_matrices.test_plot_generated_contact_matrix(setting_code=code,
                                                                                  population=expected,
                                                                                  title_prefix="Baseline_",
                                                                                  density_or_frequency=type)
                #fig.show()
                fig.savefig(os.path.join(self.figDir,f"{prefix}_{code}_{type}_expected.png"))
                fig = plot_age_mixing_matrices.test_plot_generated_contact_matrix(setting_code=code,
                                                                                  population=actual,
                                                                                  title_prefix="Actual_",
                                                                                  density_or_frequency=type)
                #fig.show()
                fig.savefig(os.path.join(self.figDir,f"{prefix}_{code}_{type}_actual.png"))

    def generate_reports(self):
        #search for config files
        configs = [f for f in os.listdir(self.configDir) if os.path.isfile(os.path.join(self.configDir, f)) and f.endswith(".txt")]
        for c in configs:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            name = os.path.splitext(c)[0]
            contents = ""
            #pdf.cell(w=200, h=10, txt=name, align="C")
            with open(os.path.join(self.configDir, c)) as cf:
                contents = "\n".join([line.strip() for line in cf])
            print(contents)
            pdf.multi_cell(w=100, h=5, txt=contents)
            for code in ['H', 'W', 'S']:
                for type in ['density', 'frequency']:
                    pdf.add_page()
                    figs = [f for f in os.listdir(self.figDir) if f.startswith(f"{name}_{code}_{type}")]
                    for ff in figs:
                        print(ff)
                        pdf.image(os.path.join(self.figDir, ff), w=100, h=100)
            pdf.output(os.path.join(self.pdfDir,f"{name}.pdf"))

    def check_similarity(self, actual, expected):
        """
        Compare two population dictionaries using contact matrix
        Assuming the canberra distance should be close to zero
        """
        for code in ['H', 'W', 'S']:
            for option in ['density', 'frequency']:
                print(f"\ncheck:{code} with {option}")
                actual_matrix = sp.calculate_contact_matrix(actual, density_or_frequency=option, setting_code=code)
                expected_matrix = sp.calculate_contact_matrix(expected, density_or_frequency=option, setting_code=code)
                # calculate Canberra distance
                # assuming they should round to 0
                d = distance.canberra(actual_matrix.flatten(), expected_matrix.flatten())
                self.assertEqual(round(d), 0, f"actual distance for {code}/{option} is {str(round(d))}, "
                                              f"you need to uncommented line 55 to plot the density matrix and investigate!")

    def cast_uid_toINT(self, dict):
        return {int(key): val for key, val in dict.items()}