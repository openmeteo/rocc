import textwrap
from io import StringIO
from unittest import TestCase

from htimeseries import HTimeseries

from rocc import Threshold, rocc


class RoccTestCase(TestCase):
    test_data = textwrap.dedent(
        """\
        2020-10-06 14:30,24.0,
        2020-10-06 14:40,25.0,
        2020-10-06 14:50,36.0,SOMEFLAG
        2020-10-06 15:01,51.0,
        2020-10-06 15:21,55.0,
        2020-10-06 15:31,65.0,
        2020-10-06 15:41,75.0,
        2020-10-06 15:51,70.0,
        """
    )

    def setUp(self):
        self.ahtimeseries = HTimeseries(StringIO(self.test_data))
        self.ahtimeseries.precision = 1
        rocc(
            timeseries=self.ahtimeseries,
            thresholds=(
                Threshold("10min", 10),
                Threshold("20min", 15),
                Threshold("H", 40),
            ),
        )

    def test_calculation(self):
        result = StringIO()
        self.ahtimeseries.write(result)
        result = result.getvalue().replace("\r\n", "\n")
        self.assertEqual(
            result,
            textwrap.dedent(
                """\
                2020-10-06 14:30,24.0,
                2020-10-06 14:40,25.0,
                2020-10-06 14:50,36.0,SOMEFLAG TEMPORAL
                2020-10-06 15:01,51.0,
                2020-10-06 15:21,55.0,
                2020-10-06 15:31,65.0,
                2020-10-06 15:41,75.0,TEMPORAL
                2020-10-06 15:51,70.0,
                """
            ),
        )

    def test_value_dtype(self):
        expected_dtype = HTimeseries().data["value"].dtype
        self.assertEqual(self.ahtimeseries.data["value"].dtype, expected_dtype)

    def test_flags_dtype(self):
        expected_dtype = HTimeseries().data["flags"].dtype
        self.assertEqual(self.ahtimeseries.data["flags"].dtype, expected_dtype)


class RoccSymmetricCase(TestCase):
    test_data = textwrap.dedent(
        """\
        2020-10-06 14:30,76.0,
        2020-10-06 14:40,75.0,SOMEFLAG
        2020-10-06 14:50,64.0,SOMEFLAG
        2020-10-06 15:01,49.0,
        2020-10-06 15:21,45.0,
        2020-10-06 15:31,35.0,
        2020-10-06 15:41,25.0,
        2020-10-06 15:51,30.0,
        """
    )

    def setUp(self):
        self.ahtimeseries = HTimeseries(StringIO(self.test_data))
        self.ahtimeseries.precision = 1

    def test_without_symmetric(self):
        rocc(
            timeseries=self.ahtimeseries,
            thresholds=(
                Threshold("10min", 10),
                Threshold("20min", 15),
                Threshold("H", 40),
            ),
        )
        result = StringIO()
        self.ahtimeseries.write(result)
        result = result.getvalue().replace("\r\n", "\n")
        self.assertEqual(
            result,
            textwrap.dedent(
                """\
                2020-10-06 14:30,76.0,
                2020-10-06 14:40,75.0,SOMEFLAG
                2020-10-06 14:50,64.0,SOMEFLAG
                2020-10-06 15:01,49.0,
                2020-10-06 15:21,45.0,
                2020-10-06 15:31,35.0,
                2020-10-06 15:41,25.0,
                2020-10-06 15:51,30.0,
                """
            ),
        )

    def test_with_symmetric(self):
        rocc(
            timeseries=self.ahtimeseries,
            thresholds=(
                Threshold("10min", 10),
                Threshold("20min", 15),
                Threshold("H", 40),
            ),
            symmetric=True,
        )
        result = StringIO()
        self.ahtimeseries.write(result)
        result = result.getvalue().replace("\r\n", "\n")
        self.assertEqual(
            result,
            textwrap.dedent(
                """\
                2020-10-06 14:30,76.0,
                2020-10-06 14:40,75.0,SOMEFLAG
                2020-10-06 14:50,64.0,SOMEFLAG TEMPORAL
                2020-10-06 15:01,49.0,
                2020-10-06 15:21,45.0,
                2020-10-06 15:31,35.0,
                2020-10-06 15:41,25.0,TEMPORAL
                2020-10-06 15:51,30.0,
                """
            ),
        )
