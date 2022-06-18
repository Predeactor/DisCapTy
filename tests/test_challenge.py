#  Copyright (c) 2022​-present - Predeactor - Licensed under the MIT License.
#  See the LICENSE file included with the file for more information about this project's
#   license.

import unittest

from discapty import Challenge, States, TooManyRetriesError, WheezyGenerator


class TestChallenge(unittest.TestCase):
    """
    Test the discapty.Challenge object.
    """

    def test_create_challenge(self):
        """
        Attempt to create a Challenge object.
        """
        challenge = Challenge(WheezyGenerator())
        self.assertIsInstance(challenge.generator, WheezyGenerator)

    def test_can_begin(self):
        """
        Attempt to begin the challenge.
        """
        challenge = Challenge(WheezyGenerator())
        challenge.begin()

        self.assertIs(challenge.state, States.WAITING)

    def test_can_be_reloaded(self):
        """
        Try to reload the Challenge's code.
        """
        challenge = Challenge(WheezyGenerator(width=500, height=300), code="wheezy")

        with self.assertRaisesRegex(TypeError, "Challenge is not running"):
            challenge.reload()

        challenge.begin()
        challenge.reload()
        self.assertEqual(challenge.attempted_tries, 1)
        self.assertNotEqual(challenge.code, "wheezy")

        challenge.reload(increase_attempted_tries=False)
        self.assertEqual(challenge.attempted_tries, 1)

    def test_ensure_captcha_is_same(self):
        """
        Ensure that the same captcha is generated each time.
        """
        challenge = Challenge(WheezyGenerator(width=500, height=300))
        first = challenge.captcha_object
        second = challenge.captcha_object
        self.assertEqual(id(first), id(second))

        challenge.code = "Anything goes!"
        third = challenge.captcha_object
        self.assertNotEqual(id(first), id(third))

    def test_challenge_validation(self):
        """
        Ensure that the Challenge returns the correct boolean when checking codes.
        """
        challenge = Challenge(WheezyGenerator(width=500, height=300), code="wheezy")

        # Testing an incorrect code
        self.assertFalse(challenge.check("whezzy"))
        self.assertIs(challenge.failures, 1)
        self.assertIs(challenge.attempted_tries, 1)

        # Testing correct code
        self.assertTrue(challenge.check("wheezy"))
        self.assertIs(challenge.failures, 1)
        self.assertIs(challenge.state, States.COMPLETED)

    def test_ensure_failures(self):
        """
        Ensure that the challenge raises an error if too many fails.
        """
        challenge = Challenge(WheezyGenerator())
        challenge.begin()

        # Testing an incorrect code
        for _ in range(challenge.allowed_retries - 1):
            challenge.check("random")

        with self.assertRaises(TooManyRetriesError):
            challenge.check("random")

    def ensure_last_failure(self):
        """
        Ensure that the challenge can handle a last sucess before failure.
        """
        challenge = Challenge(WheezyGenerator())
        challenge.begin()

        # Testing an incorrect code
        for _ in range(challenge.allowed_retries - 1):
            challenge.check("random")

        self.assertTrue(challenge.check(challenge.code))


if __name__ == "__main__":
    unittest.main()
