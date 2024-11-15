#!/usr/bin/python3

import os
import sys
import unittest
import pwd

sys.path.append(os.path.abspath('../nydus-client'))
from common import *

class TestMinecraftPath(unittest.TestCase):

    def test_find(self):

        uid = os.getuid()
        username = pwd.getpwuid(uid).pw_name

        expected = "/home/{}/.minecraft".format(username)

        self.assertEqual(expected, get_minecraft_path())

class TestStrictLstrip(unittest.TestCase):

    def test_type1(self):
        with self.assertRaises(AssertionError):
            strict_lstrip("poogah", 1)

    def test_type2(self):
        with self.assertRaises(AssertionError):
            strict_lstrip("poogah", True)

    def test_type3(self):
        with self.assertRaises(AssertionError):
            strict_lstrip("poogah", [])

    def test_type4(self):
        with self.assertRaises(AssertionError):
            strict_lstrip(0.22, "cut")

    def test_type5(self):
        with self.assertRaises(AssertionError):
            strict_lstrip(1, "cut")

    def test_type6(self):
        with self.assertRaises(AssertionError):
            strict_lstrip(True, "cut")

    def test_type7(self):
        with self.assertRaises(AssertionError):
            strict_lstrip([], "cut")

    def test_type8(self):
        with self.assertRaises(AssertionError):
            strict_lstrip(0.22, "cut")

    def test_absent(self):
        self.assertEqual(strict_lstrip("notinhere", "yes"), "notinhere")

    def test_thog(self):
        self.assertEqual(strict_lstrip("https://thog.com", "https://"), "thog.com")

    def test_google(self):
        self.assertEqual(strict_lstrip("https:google", "ht"), "tps:google")

    def test_overrun(self):
        self.assertEqual(strict_lstrip("sisters", "sisters, cousins"), "sisters")

    def test_caps(self):
        self.assertEqual(strict_lstrip("HoW dArE", "hOw"), "HoW dArE")

    def test_symbols(self):
        self.assertEqual(strict_lstrip("../?[]", "../"), "?[]")

class TestStrictRstrip(unittest.TestCase):

    def test_type1(self):
        with self.assertRaises(AssertionError):
            strict_rstrip("poogah", 1)

    def test_type2(self):
        with self.assertRaises(AssertionError):
            strict_rstrip("poogah", True)

    def test_type3(self):
        with self.assertRaises(AssertionError):
            strict_rstrip("poogah", [])

    def test_type4(self):
        with self.assertRaises(AssertionError):
            strict_rstrip(0.22, "cut")

    def test_type5(self):
        with self.assertRaises(AssertionError):
            strict_rstrip(1, "cut")

    def test_type6(self):
        with self.assertRaises(AssertionError):
            strict_rstrip(True, "cut")

    def test_type7(self):
        with self.assertRaises(AssertionError):
            strict_rstrip([], "cut")

    def test_type8(self):
        with self.assertRaises(AssertionError):
            strict_rstrip(0.22, "cut")

    def test_absent(self):
        self.assertEqual(strict_rstrip("notinhere", "yes"), "notinhere")

    def test_py(self):
        self.assertEqual(strict_rstrip("nydus.py", ".py"), "nydus")

    def test_repeat(self):
        self.assertEqual(strict_rstrip("myovermyovermyover", "myover"), "myovermyover")

    def test_double(self):
        self.assertEqual(strict_rstrip("colloquial", "loquial"), "col")

    def test_mismatch(self):
        self.assertEqual(strict_rstrip("aabcdddeeeffffg", "dddeeffffg"), "aabcdddeeeffffg")

    def test_special(self):
        self.assertEqual(strict_rstrip("!-+=_./?", "_./?"), "!-+=")

    def test_overrun(self):
        self.assertEqual(strict_rstrip("can't strip", "can't strip because the string's too long"), "can't strip")

    def test_capital1(self):
        self.assertEqual(strict_rstrip("Can You Capitalize rRight?", "Right?"), "Can You Capitalize r")

    def test_capital2(self):
        self.assertEqual(strict_rstrip("I SHOUT LOUD", " LOUD"), "I SHOUT")

if __name__ == "__main__":
    unittest.main()
