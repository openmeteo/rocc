# cython: language_level=3

from cpython cimport array
import array

cimport numpy as np
import numpy as np
import pandas as pd


class Rocc:
    def __init__(self, timeseries, thresholds, symmetric, flag):
        self.htimeseries = timeseries
        self.thresholds = thresholds
        self.symmetric = symmetric
        self.flag = flag

    def execute(self):
        self._transform_thresholds()
        self._transform_to_plain_numpy()
        self._do_actual_job()
        self._transform_to_pandas()

    def _transform_thresholds(self):
        threshold_deltas = array.array("l")
        threshold_allowed_diffs = array.array("d")

        for threshold in self.thresholds:
            threshold_deltas.append(self._get_delta_t_transformed(threshold.delta_t))
            threshold_allowed_diffs.append(threshold.allowed_diff)
        self.threshold_deltas = threshold_deltas
        self.threshold_allowed_diffs = threshold_allowed_diffs

    def _get_delta_t_transformed(self, delta_t):
        if not delta_t[0].isdigit():
            delta_t = "1" + delta_t
        return pd.Timedelta(delta_t).to_timedelta64()

    def _transform_to_plain_numpy(self):
        flag_lengths = self.htimeseries.data["flags"].str.len()
        max_flag_length = 0 if flag_lengths.empty else max(flag_lengths)
        flags_dtype = "U" + str(max_flag_length + 1 + len(self.flag))
        self.ts_index = self.htimeseries.data.index.values.astype(long)
        self.ts_values = self.htimeseries.data["value"].values
        self.ts_flags = self.htimeseries.data["flags"].values.astype(flags_dtype)

    def _do_actual_job(self):
        _perform_rocc(
            self.ts_index,
            self.ts_values,
            self.ts_flags,
            self.threshold_deltas,
            self.threshold_allowed_diffs,
            self.symmetric,
            self.flag,
        )

    def _transform_to_pandas(self):
        self.htimeseries.data = pd.DataFrame(
            index=self.htimeseries.data.index,
            columns=["value", "flags"],
            data=np.vstack((self.ts_values, self.ts_flags)).transpose(),
        )
        self.htimeseries.data["value"] = self.htimeseries.data["value"].astype(np.float64)


def _perform_rocc(
    np.ndarray ts_index,
    np.ndarray ts_values,
    np.ndarray ts_flags,
    array.array threshold_deltas,
    array.array threshold_allowed_diffs,
    int symmetric,
    str flag,
):
    cdef int i, record_fails_check

    for i in range(ts_index.size):
        record_fails_check = _record_fails_check(
            i,
            ts_index,
            ts_values,
            threshold_deltas,
            threshold_allowed_diffs,
            symmetric,
        )
        if record_fails_check:
            _add_flag(i, ts_flags, flag)


def _add_flag(int i, np.ndarray ts_flags, str flag):
    if ts_flags[i]:
        ts_flags[i] = ts_flags[i] + " "
    ts_flags[i] = ts_flags[i] + flag


def _record_fails_check(
    int record_index,
    np.ndarray ts_index,
    np.ndarray ts_values,
    array.array threshold_deltas,
    array.array threshold_allowed_diffs,
    int symmetric,
):
    cdef int ti

    for ti in range(len(threshold_deltas)):
        record_fails_threshold = _record_fails_threshold(
            record_index,
            threshold_deltas[ti],
            threshold_allowed_diffs[ti],
            ts_index,
            ts_values,
            symmetric,
        )
        if record_fails_threshold:
            return True
    return False


def _record_fails_threshold(
    int record_index,
    long threshold_delta,
    double threshold_allowed_diff,
    np.ndarray ts_index,
    np.ndarray ts_values,
    int symmetric,
):
    cdef double current_value = ts_values[record_index]
    cdef long current_timestamp = ts_index[record_index]
    cdef int i

    for i in range(record_index - 1, -1, -1):
        if current_timestamp - ts_index[i] > threshold_delta:
            return False
        if _difference(current_value, ts_values[i], symmetric) > threshold_allowed_diff:
            return True
    return False


def _difference(double a, double b, int use_abs):
    cdef double result = a - b
    if result < 0 and use_abs:
        result = -result
    return result
