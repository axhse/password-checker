import re
from enum import Enum
from typing import List


class PasswordStrength(Enum):
    """Password strength."""

    WEAK = "weak"
    """The password is weak."""

    STRONG = "strong"
    """The password is strong."""


class PasswordStrengthRuleViolation(Enum):
    """Password strength rule violation."""

    TOO_SHORT = "TOO_SHORT"
    """The password is too short."""

    TOO_MONOTONOUS = "TOO_MONOTONOUS"
    """The password lacks enough different symbols."""

    SINGLE_CATEGORY = "SINGLE_CATEGORY"
    """All symbols of the password are from the same category."""


class PasswordStrengthCheckResult:
    """Password strength check result."""

    def __init__(
        self,
        strength: PasswordStrength,
        rule_violations: List[PasswordStrengthRuleViolation],
    ):
        """
        Initialize a new PasswordStrengthCheckResult instance.

        :param strength: The strength of the password.
        :param rule_violations: A list of password strength rule violations.
        """
        self.__strength: PasswordStrength = strength
        self.__violated_rules: List[PasswordStrengthRuleViolation] = rule_violations

    @property
    def strength(self) -> PasswordStrength:
        """
        Get the strength of the password.
        :return: The strength of the password.
        """
        return self.__strength

    @property
    def violated_rules(self) -> List[PasswordStrengthRuleViolation]:
        """
        Get a list of password strength rule violations.
        :return: A list of password strength rule violations.
        """
        return self.__violated_rules


class PasswordStrengthChecker:
    """Checks the strength of passwords."""

    @staticmethod
    def check(password: str) -> PasswordStrengthCheckResult:
        """
        Check the strength of a password.

        :param password: The password to be checked.
        :return: The password strength check result.
        """
        rule_violations = list()
        if len(password) < 8:
            rule_violations.append(PasswordStrengthRuleViolation.TOO_SHORT)
        if len(set(password)) < 5:
            rule_violations.append(PasswordStrengthRuleViolation.TOO_MONOTONOUS)
        if (
            password.isdigit()
            or re.match(r"^[a-z]+$", password)
            or re.match(r"^[A-Z]+$", password)
        ):
            rule_violations.append(PasswordStrengthRuleViolation.SINGLE_CATEGORY)
        strength = (
            PasswordStrength.STRONG
            if len(rule_violations) == 0
            else PasswordStrength.WEAK
        )
        return PasswordStrengthCheckResult(strength, rule_violations)
