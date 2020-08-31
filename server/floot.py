"""
This class exports a Floot class that, unsurprisingly, represents a Floot. You
don't need to understand exactly how this class is implemented, but you should
read the method headers and their associated method comments to understand how
to use the Floot class.
"""

import uuid
from datetime import datetime, timezone
from floot_comment import FlootComment

class Floot:

    DATE_FORMAT = "%a %b %d %H:%M:%S %Y"

    # Floot Dictionary Constants
    FLOOT_ID = "id"
    MESSAGE = "message"
    TIMESTAMP = "timestamp"
    FLOOT_USERNAME = "username"
    LIKED_BY = "liked_by"
    LIKED = "liked"
    LIKES = "likes"
    COMMENTS = "comments"

    def __init__(self, message, username, liked_by=None,
                 floot_id=None, timestamp=None, comments=None):
        """
        Creates a Floot with the given parameters.

        message: the text contained in this Floot.
        username: identifies the person who wrote this Floot.

        NOTE TO STUDENT: when you call the constructor, you only need to
        specify the message and username. The other arguments are used by our
        code, but won't be useful to you.
        """
        self._message = message
        self._username = username
        self._liked_by = [] if liked_by is None else liked_by

        # Optionally set timestamp, floot_id, and comments if specified.
        # This option would only be used when Floots are being
        # recreated on reload of database. Students should NOT
        # use the constructor to set timestamp, floot_id, or comments.
        if not timestamp:
            self._timestamp = datetime.now()
        else:
            # Provided timestamp param is a string.
            # Convert it to datetime object.
            self._timestamp = datetime.strptime(timestamp, self.DATE_FORMAT)

        if not floot_id:
            self._id = str(uuid.uuid4())
        else:
            self._id = floot_id

        if not comments:
            self._comments = []
        else:
            self._comments = comments

    def get_timestamp(self):
        """Returns timestamp of when this Floot was created as a string."""
        return self._timestamp.strftime(self.DATE_FORMAT)

    def get_timestamp_raw(self):
        """Returns the timestamp of this Floot as a datetime object"""
        return self._timestamp

    def get_comments(self):
        """
        Returns a list of comments associated with this Floot. Each entry in
        the returned list is of type FlootComment. The list is sorted from
        oldest to newest comment.
        """
        return self._comments[:]

    def get_id(self):
        """Returns this Floot's unique id (string)."""
        return self._id

    def get_username(self):
        """Returns the username of this Floot's creator."""
        return self._username

    def delete_comment(self, comment, username):
        """
        Deletes the comment (of type FlootComment) from this Floot if that
        comment was written by username. If the provided comment is not a
        comment on this floot, a KeyError is raised. If `username` did not post
        this comment (and therefore isn't allowed to delete it), a
        PermissionError is raised.
        """
        if comment not in self._comments:
            raise KeyError(f"No comment with id {comment.get_id()} found in Floot with id {self._id}")

        if comment.get_author() != username:
            raise PermissionError(f"Comment with id {comment.get_id()} has username {comment.get_author()} but {username} was provided")

        self._comments.remove(comment)

    def create_comment(self, comment):
        """
        Adds comment (of type FlootComment) to this Floot.
        """
        self._comments.append(comment)

    def set_liked(self, user, liked):
        """
        Notes that the given user likes (or doesn't like) this Floot.
        """
        already_liked = user in self._liked_by
        if already_liked and not liked:
            self._liked_by.remove(user)
        elif not already_liked and liked:
            self._liked_by.append(user)

    def get_liked_by(self):
        """
        Returns a list of users who like this Floot.
        """
        return self._liked_by[:]

    def get_num_likes(self):
        """
        Returns the number of users who like this floot.
        """
        return len(self._liked_by)

    def to_dictionary(self):
        """
        Returns a dictionary where the keys are field names and the values are
        the values of the fields. Use this if you want a dictionary
        representing a Floot.
        """
        return {
            self.FLOOT_ID:       self._id,
            self.MESSAGE:        self._message,
            self.TIMESTAMP:      self.get_timestamp(),
            self.FLOOT_USERNAME: self._username,
            self.LIKED_BY:       self._liked_by,
            self.COMMENTS:       [comm.to_dictionary() for comm in self._comments]
        }

    @staticmethod
    def from_dictionary(floot_dict):
        """
        Opposite of to_dictionary.

        STUDENTS: You don't need to use this method.
        """
        floot_id = floot_dict[Floot.FLOOT_ID]
        message = floot_dict[Floot.MESSAGE]
        timestamp = floot_dict[Floot.TIMESTAMP]
        username = floot_dict[Floot.FLOOT_USERNAME]
        liked_by = floot_dict[Floot.LIKED_BY]

        # comments is a list of dictionaries, each of which represents a FlootComment.
        comments = [FlootComment.from_dictionary(c) for c in floot_dict[Floot.COMMENTS]]

        return Floot(message, username, liked_by, floot_id, timestamp, comments)

    def __str__(self):
        return "<Floot(" + str(self.to_dictionary()) + ")>"

    def __repr__(self):
        return str(self)
