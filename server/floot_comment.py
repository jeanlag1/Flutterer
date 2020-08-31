"""
This file exports a FlootComment class that, unsurprisingly, is used to
represent a comment of a floot. You don't need to understand how this class is
implemented, but you should read the method headers and their corresponding
method comments to understand how to use this class.
"""

from datetime import datetime, timezone
import uuid

class FlootComment:
    # Dictionary constants
    COMMENT_ID = "id"
    COMMENT_TEXT = "message"
    COMMENT_AUTHOR = "username"

    def __init__(self, message, author, comment_id=None):
        """
        Creates a FlootComment with the provided message (i.e. text of the
        comment itself) and author (i.e. the username of the person who wrote
        that comment).

        NOTE TO STUDENTS: You only need to specify the message and author.
        Ignore the comment_id parameter; it will be created for you.
        """
        self._message = message
        self._author = author

        # Optionally set comment id if specified.  This option would only be
        # used when FlootComments are being recreated on reload of database.
        # Students should NOT use these options to set comment_id.
        if not comment_id:
            self._id = str(uuid.uuid4())
        else:
            self._id = comment_id

    def get_id(self):
        """Returns the id of this comment (string)."""
        return self._id

    def get_author(self):
        """
        Returns the author of this comment (i.e. username of the person who
        wrote this comment).
        """
        return self._author

    def to_dictionary(self):
        """
        Returns a dictionary where the keys are field names and the values are
        the values of the fields. Use this if you want a dictionary
        representing a FlootComment.
        """
        return {
            self.COMMENT_ID:     self._id,
            self.COMMENT_TEXT:   self._message,
            self.COMMENT_AUTHOR: self._author
        }

    @staticmethod
    def from_dictionary(fields):
        """
        Opposite of to_dictionary.

        STUDENTS: You don't need to use this method.
        """
        comment_id = fields[FlootComment.COMMENT_ID]
        message = fields[FlootComment.COMMENT_TEXT]
        author = fields[FlootComment.COMMENT_AUTHOR]
        return FlootComment(message, author, comment_id)

    def __str__(self):
        return f"<FlootComment({self._message}, {self._author}, {self._id})>"

    def __repr__(self):
        return str(self)
