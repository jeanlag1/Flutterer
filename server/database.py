"""
This file exports a Database class that you can use to store Floots. You can
create a new Database object like so:

database = Database()

Changes made to the Database will persist even if you shut down your Python
program and restart it. (It will also work even if you restart your computer!)

You don't need to understand how the Database class is implemented, but you
should read through the public method headers (i.e. the ones that don't start
with an underscore) and read their associated method comments to understand how
to use the Database class.
"""

import json
import os
from floot import Floot
from datetime import datetime

DATE_FORMAT = "%a %b %d %H:%M:%S %Y"

class Database:
    def __init__(self, db_path=None):
        """
        Constructs a new Database
        """
        if not db_path:
            db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         "data.json")
        self._db_path = db_path
        self._data = {}
        if os.path.exists(self._db_path):
            self._load_data_from_file()

    def _load_data_from_file(self):
        """
        Students: Don't call this method.
        """
        with open(self._db_path, "r") as f:
            parsed_file = json.load(f)

        for floot_id, floot_dict in parsed_file.items():
            self._data[floot_id] = Floot.from_dictionary(floot_dict)

    def _write_data_to_file(self):
        """
        Students: don't call this method.
        """
        with open(self._db_path, "w") as f:
            json.dump({floot_id: floot.to_dictionary()
                       for floot_id, floot in self._data.items()}, f, indent=4)

    def get_floots(self, count=None):
        """
        Returns a list of Floot objects, containing no more than `count`
        Floots. If count is unspecified, returns a list of all the Floots. If
        count is specified, the most recent `count` floots are returned.
        Floots in the returned list are sorted from newest to oldest.
        """
        if count is None:
            count = len(self._data)

        floots = list(self._data.values())
        floots = sorted(floots, key=lambda f: f.get_timestamp_raw(), reverse=True)

        return floots[:count]

    def has_floot(self, floot_id):
        """
        Takes a floot ID and returns True if that ID exists in the database,
        and False if it does not.
        """
        return floot_id in self._data

    def get_floot_by_id(self, floot_id):
        """
        Takes a floot id and returns the floot object with that ID. Note: IDs
        are unique. Raises a KeyError if no floot has the provided floot_id.
        """
        try:
            return self._data[floot_id]
        except KeyError:
            raise KeyError(f"No floot with id {floot_id} in database")

    def save_floot(self, floot):
        """
        Saves the provided floot (of type Floot) into the database. You can
        call this multiple times on the same Floot; it will replace old data
        and save the latest version of the Floot.

        You will also need to call this method to re-save a floot if you add or
        remove comments from that Floot.
        """
        self._data[floot.get_id()] = floot
        self._write_data_to_file()

    def delete_floot_by_id(self, floot_id):
        """
        Attempts to delete the floot with provided id.  Raises a KeyError if
        provided id doesn't exist in the database.
        """
        try:
            del self._data[floot_id]
            self._write_data_to_file()
        except:
            raise KeyError(f"No floot with id {floot_id} in database")

    def delete_floot(self, floot):
        """
        Attempts to delete the provided floot (of type Floot). Raises a
        KeyError if provided Floot is not in the database.
        """
        self.delete_floot_by_id(floot.get_id())

    def __str__(self):
        return "<FlootDatabase(" + str(self._data) + ")>"

    def __repr__(self):
        return str(self)
