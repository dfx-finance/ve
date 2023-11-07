#!/usr/bin/env python
from colorama import Fore, Style


class _Checker:
    PASS_TEXT = Fore.GREEN + "PASS - {msg}" + Style.RESET_ALL
    FAIL_TEXT = Fore.RED + "FAIL - {msg}" + Style.RESET_ALL
    PASS_DEBUG_TEXT = Fore.YELLOW + "PASS - {msg} (debug)" + Style.RESET_ALL
    FAIL_DEBUG_TEXT = Fore.MAGENTA + "FAIL - {msg} (debug)" + Style.RESET_ALL

    def _value(self, test_val, expected_val, label, debug_val=None):
        inner = f"{label}: {test_val}"
        if debug_val:
            if test_val == debug_val:
                print(self.PASS_DEBUG_TEXT.format(msg=inner))
            else:
                print(self.FAIL_DEBUG_TEXT.format(msg=inner))
            return

        if test_val == expected_val:
            print(self.PASS_TEXT.format(msg=inner))
        else:
            print(self.FAIL_TEXT.format(msg=inner))

    def address(self, test_addr, expected_addr, label, debug_addr=None):
        Checker._value(test_addr, expected_addr, label, debug_addr)

    def number(self, test_num, expected_num, label):
        Checker._value(test_num, expected_num, label)

    def number_gt(self, test_num, expected_num, label):
        inner = f"{label}: {test_num}"
        if test_num > expected_num:
            print(self.PASS_TEXT.format(msg=inner))
        else:
            print(self.FAIL_TEXT.format(msg=inner))

    def number_lt(self, test_num, expected_num, label):
        inner = f"{label}: {test_num}"
        if test_num < expected_num:
            print(self.PASS_TEXT.format(msg=inner))
        else:
            print(self.FAIL_TEXT.format(msg=inner))

    def has_role(self, contract, role, test_addr, label, reverse=False):
        _has_role = contract.has_role(role, test_addr)
        if reverse:
            _has_role = not _has_role
        if _has_role:
            print(self.PASS_TEXT.format(msg=f"{label}: {test_addr} has role"))
        else:
            print(self.FAIL_TEXT.format(msg=f"{label}: {test_addr} missing role"))


Checker = _Checker()
