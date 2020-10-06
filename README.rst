===========================================
rocc - Rate-of-change check for time series
===========================================


.. image:: https://img.shields.io/pypi/v/rocc.svg
        :target: https://pypi.python.org/pypi/rocc

.. image:: https://img.shields.io/travis/openmeteo/rocc.svg
        :target: https://travis-ci.org/openmeteo/rocc

.. image:: https://codecov.io/github/openmeteo/rocc/coverage.svg
        :target: https://codecov.io/gh/openmeteo/rocc
        :alt: Coverage

.. image:: https://pyup.io/repos/github/openmeteo/rocc/shield.svg
         :target: https://pyup.io/repos/github/openmeteo/rocc/
         :alt: Updates

::

   from rocc import rocc

   rocc(
      timeseries=a_pandas_time_series,
      thresholds=(
         Threshold("10min", 10),
         Threshold("20min", 15),
         Threshold("H", 40),
      ),
      symmetric=True,
      flag="MYFLAG",
   )

``timeseries`` is a pandas time series (dataframe) with a single column
(besides the index). ``thresholds`` is, obviously, a list of thresholds.
``Threshold`` is a named tuple whose items are ``delta_t`` (a pandas
interval specification) and ``allowed_diff`` (a floating point number).

The function checks whether there exist intervals during which the value
of the time series changes by more than the specified threshold. All
records of that interval are flagged with the specified ``flag``
(the default ``flag`` is ``TEMPORAL``).

Here is an example time series::

    2020-10-06 14:30    24.0
    2020-10-06 14:40    25.0 *
    2020-10-06 14:50    36.0 *
    2020-10-06 15:01    52.0
    2020-10-06 15:21    55.0 *
    2020-10-06 15:31    65.0 *
    2020-10-06 15:41    75.0 *
    2020-10-06 15:51    70.0

After running ``rocc()`` with the ``thresholds`` specified in the
example above, the records marked with a star will be flagged. The
records ``14:40`` and ``14:50`` will be flagged because they define a
10-minute interval in which the value increases by 11, which is more
than 10. The three records ``15:21``-``15:41`` will be flagged because
they define a 20-minute interval in which the value increases by 20,
which is more than 15. The record ``15:01`` will be unflagged; although
there's a large difference since ``14:40``, this is 21 minutes, not 20,
so the 20-minute threshold of 15 does not apply; neither is there any
difference larger than 40 within an hour anywhere.

If ``symmetric`` is ``True``, it is the absolute value of the change
that matters, not its direction. In this case, ``allowed_diff`` must be
positive. If ``symmetric`` is ``False`` (the default), only rates larger
than positive ``allow_diff`` or rates smaller than negative
``allow_diff`` are flagged.
