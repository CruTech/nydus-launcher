#!/usr/bin/python3

import unittest

from nydus.common.validity import *

class TestValidIPaddr(unittest.TestCase):

    def test_simple(self):
        self.assertTrue(is_valid_ipaddr("192.168.1.1"))

    def test_crutech(self):
        self.assertTrue(is_valid_ipaddr("192.168.67.253"))

    def test_min(self):
        self.assertTrue(is_valid_ipaddr("0.0.0.0"))

    def test_max(self):
        self.assertTrue(is_valid_ipaddr("255.255.255.255"))

    def test_under1(self):
        self.assertFalse(is_valid_ipaddr("-1.4.16.200"))

    def test_under2(self):
        self.assertFalse(is_valid_ipaddr("1.-4.16.200"))

    def test_under3(self):
        self.assertFalse(is_valid_ipaddr("1.4.-16.200"))

    def test_under4(self):
        self.assertFalse(is_valid_ipaddr("1.4.16.-200"))

    def test_over1(self):
        self.assertFalse(is_valid_ipaddr("256.13.144.69"))

    def test_over2(self):
        self.assertFalse(is_valid_ipaddr("10.999.144.69"))

    def test_over3(self):
        self.assertFalse(is_valid_ipaddr("10.13.1044.69"))

    def test_over4(self):
        self.assertFalse(is_valid_ipaddr("10.13.144.652"))

    def test_short(self):
        self.assertFalse(is_valid_ipaddr("155.253.67"))

    def test_long(self):
        self.assertFalse(is_valid_ipaddr("155.253.67.90.216"))

    def test_alph1(self):
        self.assertFalse(is_valid_ipaddr("a5.155.253.67"))

    def test_alph2(self):
        self.assertFalse(is_valid_ipaddr("5.1YY.253.67"))

    def test_alph3(self):
        self.assertFalse(is_valid_ipaddr("5.155.5e3.67"))

    def test_alph4(self):
        self.assertFalse(is_valid_ipaddr("5.155.253.6P"))

    def test_alph(self):
        self.assertFalse(is_valid_ipaddr("A2.b3.4F.L9"))

    def test_nodots(self):
        self.assertFalse(is_valid_ipaddr("1019914469"))


class TestValidPort(unittest.TestCase):
    
    def test_min(self):
        self.assertTrue(is_valid_port("0"))

    def test_max(self):
        self.assertTrue(is_valid_port(str(2**16 - 1)))

    def test_intmin(self):
        self.assertFalse(is_valid_port(0))

    def test_intmax(self):
        self.assertFalse(is_valid_port(2**16 - 1))

    def test_under(self):
        self.assertFalse(is_valid_port("-1"))

    def test_over(self):
        self.assertFalse(is_valid_port(str(2**16)))

    def test_admin(self):
        self.assertTrue(is_valid_port("1024"))

    def test_ssh(self):
        self.assertTrue(is_valid_port("22"))

    def test_nydus(self):
        self.assertTrue(is_valid_port("2011"))

    def test_type1(self):
        self.assertFalse(is_valid_port(8036))

    def test_type2(self):
        self.assertFalse(is_valid_port(True))

    def test_type3(self):
        self.assertFalse(is_valid_port(["2011"]))

    def test_type4(self):
        self.assertFalse(is_valid_port(78.0))


class TestInteger(unittest.TestCase):

    def test_pos(self):
        self.assertTrue(is_integer("12345"))

    def test_neg(self):
        self.assertTrue(is_integer("-9582"))

    def test_zero(self):
        self.assertTrue(is_integer("0"))

    def test_int(self):
        self.assertFalse(459)

    def test_bool(self):
        self.assertFalse(True)

    def test_list(self):
        self.assertFalse(["23", "45"])

    def test_float(self):
        self.assertFalse(9554.00)


class TestPosInteger(unittest.TestCase):

    def test_pos(self):
        self.assertTrue(is_positive_integer("12345"))

    def test_neg(self):
        self.assertFalse(is_positive_integer("-9582"))

    def test_one(self):
        self.assertTrue(is_positive_integer("1"))

    def test_minusone(self):
        self.assertFalse(is_positive_integer("-1"))

    def test_zero(self):
        self.assertFalse(is_positive_integer("0"))

    def test_int(self):
        self.assertFalse(is_positive_integer(459))

    def test_bool(self):
        self.assertFalse(is_positive_integer(True))

    def test_list(self):
        self.assertFalse(is_positive_integer(["23", "45"]))

    def test_float(self):
        self.assertFalse(is_positive_integer(9554.00))


class TestNonNegInteger(unittest.TestCase):

    def test_pos(self):
        self.assertTrue(is_nonnegative_integer("12345"))

    def test_neg(self):
        self.assertFalse(is_nonnegative_integer("-9582"))

    def test_one(self):
        self.assertTrue(is_nonnegative_integer("1"))

    def test_minusone(self):
        self.assertFalse(is_nonnegative_integer("-1"))

    def test_zero(self):
        self.assertTrue(is_nonnegative_integer("0"))

    def test_int(self):
        self.assertFalse(is_nonnegative_integer(459))

    def test_bool(self):
        self.assertFalse(is_nonnegative_integer(True))

    def test_list(self):
        self.assertFalse(is_nonnegative_integer(["23", "45"]))

    def test_float(self):
        self.assertFalse(is_nonnegative_integer(9554.00))


class TestLimitedInteger(unittest.TestCase):

    def test_mid(self):
        self.assertTrue(is_limited_integer("5", 1, 10))

    def test_bot(self):
        self.assertTrue(is_limited_integer("1", 1, 10))

    def test_top(self):
        self.assertTrue(is_limited_integer("10", 1, 10))

    def test_over(self):
        self.assertFalse(is_limited_integer("11", 1, 10))

    def test_under(self):
        self.assertFalse(is_limited_integer("0", 1, 10))

    def test_neg_mid(self):
        self.assertTrue(is_limited_integer("-20", -35, -11))

    def test_neg_bot(self):
        self.assertTrue(is_limited_integer("-35", -35, -11))

    def test_neg_top(self):
        self.assertTrue(is_limited_integer("-11", -35, -11))

    def test_neg_over(self):
        self.assertFalse(is_limited_integer("-10", -35, -11))

    def test_neg_under(self):
        self.assertFalse(is_limited_integer("-36", -35, -11))

    def test_wide_pos(self):
        self.assertTrue(is_limited_integer("350", -1200, 1820))

    def test_wide_neg(self):
        self.assertTrue(is_limited_integer("-950", -1200, 1820))

    def test_wide_mid(self):
        self.assertTrue(is_limited_integer("310", -1200, 1820))

    def test_wide_zero(self):
        self.assertTrue(is_limited_integer("0", -1200, 1820))

    def test_wide_over(self):
        self.assertFalse(is_limited_integer("1821", -1200, 1820))

    def test_wide_under(self):
        self.assertFalse(is_limited_integer("-1201", -1200, 1820))

    def test_wide_farover(self):
        self.assertFalse(is_limited_integer("3218", -1200, 1820))

    def test_wide_farunder(self):
        self.assertFalse(is_limited_integer("-1786", -1200, 1820))

    def test_int(self):
        self.assertFalse(is_limited_integer(19))

    def test_bool(self):
        self.assertFalse(is_limited_integer(False))

    def test_list(self):
        self.assertFalse(is_limited_integer(["88434", "11111"]))

    def test_float(self):
        self.assertFalse(is_limited_integer(9248.00))


class TestVersion(unittest.TestCase):

    def test_two(self):
        self.assertTrue(is_valid_version("1.0", 2))

    def test_three(self):
        self.assertTrue(is_valid_version("1.0.0", 3))

    def test_four(self):
        self.assertTrue(is_valid_version("1.0.0.0", 4))

    def test_five(self):
        self.assertTrue(is_valid_version("1.0.0.0.0", 5))

    def test_complex(self):
        self.assertTrue(is_valid_version("2.18.9", 3))

    def test_neg(self):
        self.assertFalse(is_valid_version("-1.0.0", 3))

    def test_empty_one(self):
        self.assertFalse(is_valid_version(".1.0", 3))

    def test_empty_two(self):
        self.assertFalse(is_valid_version("2..5", 3))

    def test_empty_three(self):
        self.assertFalse(is_valid_version("1.3.", 3))


class TestMinecraftVersion(unittest.TestCase):

    def test_simple1(self):
        self.assertTrue("1.20.4")

    def test_simple2(self):
        self.assertTrue("1.20.6")

    def test_simple3(self):
        self.assertTrue("1.21.4")

    def test_opti1(self):
        self.assertTrue("1.20.4-OptiFine_HD_U_I7")

    def test_opti2(self):
        self.assertTrue("1.21.3-OptiFine_HD_U_J2")

    def test_rc1(self):
        self.assertTrue("1.21-rc1")

    def test_rc2(self):
        self.assertTrue("1.21.4-rc3")

    def test_rc2(self):
        self.assertTrue("1.20-rc1")

    def test_pre1(self):
        self.assertTrue("1.21.4-pre2")

    def test_pre2(self):
        self.assertTrue("1.20.3-pre4")

    def test_pre3(self):
        self.assertTrue("1.20-pre6")

if __name__ == "__main__":
    unittest.main()
