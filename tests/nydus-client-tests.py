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

class TestIsSha1(unittest.TestCase):

    def test_sample1(self):
        self.assertTrue(is_sha1("b1d8ab82d11d92fd639b56d639f8f46f739dd5fa"))
        
    def test_sample2(self):
        self.assertTrue(is_sha1("659feffdd12280201c8aacb8f7be94f9a883c824"))

    def test_sample3(self):
        self.assertTrue(is_sha1("ba1f3fed0ee4be0217eaa41c5bbfb4b9b1383c33"))

    def test_sample4(self):
        self.assertTrue(is_sha1("2351fc2fc174c27300e404ab038b88a54cc32455"))

    def test_sample5(self):
        self.assertTrue(is_sha1("da2bc4e9f46906f7199a8ac661e08d64c6bc28f4"))

    def test_fail1(self):
        self.assertFalse(is_sha1("b1d8ab82d11d92fd639b56d639f8f46f739dd5fa4"))
        
    def test_fail2(self):
        self.assertFalse(is_sha1("659f-ffdd122+0201c8aacb8f7be94f9a883c824"))

    def test_fail3(self):
        self.assertFalse(is_sha1("ba1f3fed!ee4be0217eaa41c5bbf  b9b1383c33"))

    def test_fail4(self):
        self.assertFalse(is_sha1("351fc2fc174c27300e404ab038b88a54cc32455"))

    def test_fail5(self):
        self.assertFalse(is_sha1(""))

    def test_type1(self):
        with self.assertRaises(AssertionError):
            is_sha1(8)

    def test_type2(self):
        with self.assertRaises(AssertionError):
            is_sha1(4725343924690617190089866170866456432824)

    def test_type3(self):
        with self.assertRaises(AssertionError):
            is_sha1(True)

    def test_type4(self):
        with self.assertRaises(AssertionError):
            is_sha1(["ba1f", "3fed0ee4be0", "217eaa41c5bbf", "b4b9b1383c33"])

    def test_type5(self):
        with self.assertRaises(AssertionError):
            is_sha1(6591234561228020168789081723944958.836824)

if __name__ == "__main__":
    unittest.main()
