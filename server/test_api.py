"""
This file contains a series of test cases you can use to ensure your api.py
implementations are correct. You don't need to understand or change any of the
code here. To run these tests, go to Run > Run 'Unittests in test_api.py'.
"""
import os
import unittest
from datetime import timedelta

import api
from database import Database
from floot import Floot
from floot_comment import FlootComment
from error import HTTPError

TEST_DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            "test_database.json")

class TestApi(unittest.TestCase):
    def setUp(self):
        """
        This function is called before every test function. Its goal is to set
        up a test database that has a few sample Floots and FlootComments.
        """
        # First, let's create an empty test database. Delete any existing test
        # database:
        if os.path.exists(TEST_DB_PATH):
            os.unlink(TEST_DB_PATH)
        self.test_db = Database(TEST_DB_PATH)

        # Add some fake floots to this database
        self.floots = [ Floot("Hello world!", "Test User 1"),
                        Floot("Hello world again!", "Test User 2") ]

        # ensures consistent ordering between floots created in the same second.
        self.floots[0]._timestamp -= timedelta(minutes=5)

        for floot in self.floots:
            self.test_db.save_floot(floot)

        # Add some comments to the first post
        self.comments = [ FlootComment("Comment 1", "Test User 1"),
                          FlootComment("Comment 2", "Test User 2") ]
        for comment in self.comments:
            self.floots[0].create_comment(comment)
            self.test_db.save_floot(self.floots[0])

        # Add one comment to the second post
        self.comments.append(FlootComment("Comment 3", "Test User 1"))
        self.floots[1].create_comment(self.comments[-1])
        self.test_db.save_floot(self.floots[1])

        # Make the api module use this database, instead of the normal one
        api.db = self.test_db

    def tearDown(self):
        """
        This function is called after every test function. It deletes the test
        database, so that the next test to be run gets a clean slate.
        """
        # Delete the test database
        if os.path.exists(TEST_DB_PATH):
            os.unlink(TEST_DB_PATH)

    def test_get_floots(self):
        """
        Verify that GET /api/floots works
        """
        api_return = api.get_floots()
        # Make sure it returns a list of dictionaries, of length 2
        self.assertIsInstance(api_return, list, "Expected api.get_floots to return a list")
        self.assertEqual(len(api_return), 2, "Expected returned list length to be 2")
        for elem in api_return:
            self.assertIsInstance(elem, dict,
                    "Expected api.get_floots to return a list of dictionaries, but "
                    "instead it's a list of " + str(type(elem)))

        # Make sure the first dictionary looks reasonable
        self.assertEqual(api_return[0]["id"], self.floots[1].get_id(),
                "Floot ID of the first floot does not seem correct! Make sure you "
                "aren't accidentally reordering the floots.")


    def test_get_floot_with_valid_id(self):
        """
        Verify that GET /api/floots/{id} works, when passed a valid ID
        """
        output = api.get_floot(self.floots[0].get_id())

        # Make sure it returns a dictionary
        self.assertIsInstance(output, dict,
                "Expected api.get_floot to return a dictionary, but instead it returned "
                "a " + str(type(output)))
        # Make sure the returned username is correct
        self.assertEqual(output["username"], self.floots[0].get_username())

    def test_get_floot_with_invalid_id(self):
        """
        Verify that a floot GET /api/floots/{id} returns an error 404 when
        passed an invalid floot ID
        """
        expectation = (
                "Expected get_floot to raise or return an HTTPError with status "
                "404 when given an invalid floot_id"
        )

        try:
            exception = api.get_floot("invalid id")
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 404
        self.assertEqual(exception.status, 404, expectation)

    def test_create_floot(self):
        """
        Verify that POST /api/floots/ works
        """
        output = api.create_floot({
            "message": "This is a new floot!",
            "username": "Brand new user",
        })

        # Make sure it returns a dictionary
        self.assertIsInstance(output, dict,
                "Expected api.create_floot to return a dictionary, but instead it "
                "returned a " + str(type(output)))

        # Make sure the "message" and "username" fields in the returned
        # dictionary match what we provided
        self.assertEqual(output["message"], "This is a new floot!")
        self.assertEqual(output["username"], "Brand new user")

        # Make sure the output dict contains a "timestamp" field (to make sure
        # that a floot dict was created, instead of just returning the input we
        # provided)
        self.assertIn("timestamp", output)

        # Make sure the floot actually got saved to the database
        self.assertTrue(self.test_db.has_floot(output["id"]),
                "Could not find the outputted ID in the database. Maybe you forgot to "
                "do db.save_floot()?")

    def test_create_floot_with_missing_message(self):
        """
        Verify that POST /api/floots returns an error 400 when missing the
        "message" parameter
        """
        expectation = (
                "Expected api.create_floot to raise or return an HTTPError with status "
                "400 when the \"message\" key is missing from `info`"
        )

        try:
            exception = api.create_floot({
                "username": "Brand new user",
            })
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 400
        self.assertEqual(exception.status, 400, expectation)

    def test_create_floot_with_missing_username(self):
        """
        Verify that POST /api/floots returns an error 400 when missing the
        "username" parameter
        """
        expectation = (
                "Expected api.create_floot to raise or return an HTTPError with status "
                "400 when the \"username\" key is missing from `info`"
        )

        try:
            exception = api.create_floot({
                "message": "This is a new floot!",
            })
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 400
        self.assertEqual(exception.status, 400, expectation)

    def test_delete_floot_with_valid_id_and_username(self):
        """
        Verify that POST /api/floots/{id}/delete works, when passed a valid ID
        and username
        """
        output = api.delete_floot(self.floots[0].get_id(), {
            "username": self.floots[0].get_username(),
        })

        # Make sure it returned "OK"
        self.assertEqual(output, "OK", "Expected function to succeed and return \"OK\"")

        # Make sure we can't find the floot in the database anymore
        self.assertFalse(self.test_db.has_floot(self.floots[0].get_id()))

    def test_delete_floot_with_invalid_id(self):
        """
        Verify that POST /api/floots/{id}/delete returns an error 404 when
        given an invalid floot ID
        """
        expectation = (
                "Expected delete_floot to raise or return an HTTPError with status "
                "404 when given an invalid floot_id"
        )

        try:
            exception = api.delete_floot("invalid id", {
                "username": self.floots[0].get_username(),
            })
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 404
        self.assertEqual(exception.status, 404, expectation)

    def test_delete_floot_with_missing_username(self):
        """
        Verify that POST /api/floots/{floot_id}/delete returns an error 400
        when missing the "username" parameter
        """
        expectation = (
                "Expected api.delete_floot to raise or return an HTTPError with status "
                "400 when the \"username\" key is missing from `info`"
        )

        try:
            exception = api.delete_floot(self.floots[0].get_id(), {})
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 400
        self.assertEqual(exception.status, 400, expectation)

    def test_delete_floot_with_incorrect_username(self):
        """
        Verify that POST /api/floots/{id}/delete returns an error 401 when
        the supplied username does not match the floot's username
        """
        expectation = (
                "Expected delete_floot to raise or return an HTTPError with status "
                "401 when given an incorrect username"
        )

        try:
            exception = api.delete_floot(self.floots[0].get_id(), {
                "username": self.floots[1].get_username(),
            })
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 401
        self.assertEqual(exception.status, 401, expectation)

    def test_get_comments_with_valid_id(self):
        """
        Verify that GET /api/floots/{id}/comments works, when passed a valid ID
        """
        output = api.get_comments(self.floots[0].get_id())

        # Make sure it returns a list of dictionaries, of length 2
        self.assertIsInstance(output, list,
                "Expected api.get_comments to return a list")
        self.assertEqual(len(output), 2,
                "Expected returned list length to be 2")
        for elem in output:
            self.assertIsInstance(elem, dict,
                    "Expected api.get_comments to return a list of dictionaries, but "
                    "instead it's a list of " + str(type(elem)))

        # Make sure the contents seem correct
        self.assertEqual(output[0]["id"], self.comments[0].get_id())
        self.assertEqual(output[1]["id"], self.comments[1].get_id())

    def test_get_comments_with_invalid_id(self):
        """
        Verify that GET /api/floots/{id}/comments returns an error 404 when
        passed an invalid floot ID
        """
        expectation = (
                "Expected api.get_comments to raise or return an HTTPError with "
                "status 404 when given an invalid floot_id"
        )

        try:
            exception = api.get_comments("invalid id")
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 404
        self.assertEqual(exception.status, 404, expectation)

    def test_create_comment_with_valid_id(self):
        """
        Verify that POST /api/floots/{id}/comments works, when passed a valid ID
        """
        output = api.create_comment(self.floots[0].get_id(), {
            "username": "Brand new user",
            "message": "This is a new comment",
        })

        # Make sure it returns a dictionary
        self.assertIsInstance(output, dict,
                "Expected api.create_comment to return a dictionary, but instead it "
                "returned a " + str(type(output)))

        # Make sure the "message" and "username" fields in the returned
        # dictionary match what we provided, and that the dict contains an "id"
        # field
        self.assertEqual(output["username"], "Brand new user")
        self.assertEqual(output["message"], "This is a new comment")
        self.assertIn("id", output)

        # Make sure the comment actually got saved to the database
        updated_floot = self.test_db.get_floot_by_id(self.floots[0].get_id())
        db_comments = updated_floot.get_comments()
        self.assertTrue(output["id"] in [ c.get_id() for c in db_comments ],
                "Could not find the outputted ID in the database. Maybe you forgot to "
                "add the FlootComment to the Floot (Floot.create_comment), or to do "
                "db.save_floot() after adding the comment to the Floot?")

    def test_create_comment_with_invalid_id(self):
        """
        Verify that POST /api/floots/{id}/comments returns an error 404 when
        passed an invalid floot ID
        """
        expectation = (
                "Expected api.create_comment to raise or return an HTTPError with "
                "status 404 when given an invalid floot_id"
        )

        try:
            exception = api.create_comment("invalid id", {
                "username": "Brand new user",
                "message": "This is a new comment",
            })
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 404
        self.assertEqual(exception.status, 404, expectation)

    def test_create_comment_with_missing_message(self):
        """
        Verify that POST /api/floots/{floot_id}/comments returns an error 400
        when missing the "message" parameter
        """
        expectation = (
                "Expected api.create_comment to raise or return an HTTPError with status "
                "400 when the \"message\" key is missing from `info`"
        )

        try:
            exception = api.create_comment(self.floots[0].get_id(), {
                "username": "Brand new user",
            })
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 400
        self.assertEqual(exception.status, 400, expectation)

    def test_create_comment_with_missing_username(self):
        """
        Verify that POST /api/floots/{floot_id}/comments returns an error 400
        when missing the "username" parameter
        """
        expectation = (
                "Expected api.create_comment to raise or return an HTTPError with status "
                "400 when the \"username\" key is missing from `info`"
        )

        try:
            exception = api.create_comment(self.floots[0].get_id(), {
                "message": "This is a new comment",
            })
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 400
        self.assertEqual(exception.status, 400, expectation)

    def test_delete_comment(self):
        """
        Verify that POST /api/floots/{floot_id}/comments/{comment_id}/delete
        works, when passed valid IDs and the correct username
        """
        output = api.delete_comment(self.floots[0].get_id(), self.comments[1].get_id(), {
            "username": self.comments[1].get_author(),
        })

        # Make sure it returned "OK"
        self.assertEqual(output, "OK", "Expected function to succeed and return \"OK\"")

        # Make sure we can't find the comment in the database anymore
        updated_floot = self.test_db.get_floot_by_id(self.floots[0].get_id())
        comments = [ c.get_id() for c in updated_floot.get_comments() ]
        self.assertTrue(self.comments[1].get_id() not in comments)

    def test_delete_comment_with_invalid_floot_id(self):
        """
        Verify that POST /api/floots/{floot_id}/comments/{comment_id}/delete
        returns an error 404 when given an invalid floot ID
        """
        expectation = (
                "Expected delete_comment to raise or return an HTTPError with status "
                "404 when given an invalid floot_id"
        )

        try:
            exception = api.delete_comment("invalid id", self.comments[0].get_id(), {
                "username": self.comments[0].get_author(),
            })
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 404
        self.assertEqual(exception.status, 404, expectation)

    def test_delete_comment_with_invalid_comment_id(self):
        """
        Verify that POST /api/floots/{floot_id}/comments/{comment_id}/delete
        returns an error 404 when given an invalid comment ID
        """
        expectation = (
                "Expected delete_comment to raise or return an HTTPError with status "
                "404 when given an invalid comment_id"
        )

        try:
            # self.comments[2] is a comment on a different post, so this should
            # fail (even though it is a comment that exists)
            exception = api.delete_comment(self.floots[0].get_id(), self.comments[2].get_id(), {
                "username": self.comments[2].get_author(),
            })
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 404
        self.assertEqual(exception.status, 404, expectation)

    def test_delete_comment_with_missing_username(self):
        """
        Verify that POST /api/floots/{floot_id}/comments/{comment_id}/delete
        returns an error 400 when missing the "username" parameter
        """
        expectation = (
                "Expected api.delete_comment to raise or return an HTTPError with status "
                "400 when the \"username\" key is missing from `info`"
        )

        try:
            exception = api.delete_comment(self.floots[0].get_id(),
                    self.comments[0].get_id(), {})
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 400
        self.assertEqual(exception.status, 400, expectation)

    def test_delete_comment_with_incorrect_username(self):
        """
        Verify that POST /api/floots/{floot_id}/comments/{comment_id}/delete
        returns an error 401 when the supplied username does not match the
        comment's username
        """
        expectation = (
                "Expected api.delete_comment to raise or return an HTTPError with status "
                "401 when given an incorrect username"
        )

        try:
            exception = api.delete_comment(self.floots[0].get_id(), self.comments[1].get_id(), {
                "username": self.floots[0].get_username(),
            })
        except HTTPError as e:
            exception = e

        # Make sure HTTPError was raised or returned
        self.assertIsInstance(exception, HTTPError, expectation)
        # Make sure the specific error is error 401
        self.assertEqual(exception.status, 401, expectation)


if __name__ == "__main__":
    unittest.main()
