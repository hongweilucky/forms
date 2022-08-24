#  Copyright 2022-2023 The FormS Authors.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import pytest

import forms
from forms.executor.pandasexecutor.functionexecutor import *

df = None


@pytest.fixture(autouse=True)
def execute_before_and_after_one_test():
    m = 100
    n = 5
    global df
    df = pd.DataFrame(np.ones((m, n)))

    forms.config(
        cores=4, scheduler="frrftwophase", enable_logical_rewriting=False, enable_physical_opt=True
    )
    yield


def test_compute_2_phase_sum_fr():
    global df
    computed_df = forms.compute_formula(df, "=SUM(A$2:B3)")
    expected_df = pd.DataFrame(np.arange(4, 200, 2))
    assert np.array_equal(computed_df.iloc[0:98].values, expected_df.values)


def test_compute_2_phase_sum_rf():
    global df
    computed_df = forms.compute_formula(df, "=SUM(A2:B$99)")
    expected_df = pd.DataFrame(np.arange(196, 2, -2))
    assert np.array_equal(computed_df.iloc[0:97].values, expected_df.values)


def test_compute_2_phase_count_fr():
    global df
    computed_df = forms.compute_formula(df, "=COUNT(A$1:B3)")
    expected_df = pd.DataFrame(np.arange(6, 202, 2))
    assert np.array_equal(computed_df.iloc[0:98].values, expected_df.values)


def test_compute_2_phase_count_rf():
    global df
    computed_df = forms.compute_formula(df, "=COUNT(A1:A$100)")
    expected_df = pd.DataFrame(np.arange(100, 0, -1))
    assert np.array_equal(computed_df.values, expected_df.values)


def test_compute_2_phase_max_fr():
    global df
    computed_df = forms.compute_formula(df, "=MAX(A$1:B3)")
    expected_df = pd.DataFrame(np.full(100, 1))
    expected_df.iloc[98:100, 0] = np.NaN
    assert np.array_equal(computed_df.values, expected_df.values, equal_nan=True)


def test_compute_2_phase_min_rf():
    global df
    computed_df = forms.compute_formula(df, "=MIN(A1:A$100)")
    expected_df = pd.DataFrame(np.full(100, 1))
    assert np.array_equal(computed_df.values, expected_df.values)


def test_compute_2_phase_avg_rf():
    global df
    computed_df = forms.compute_formula(df, "=AVERAGE(A1:A$100)")
    expected_df = pd.DataFrame(np.full(100, 1))
    assert np.array_equal(computed_df.values, expected_df.values)
