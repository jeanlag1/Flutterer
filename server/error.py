class HTTPError(Exception):
    """
    This exception class is used to tell the client that something went wrong
    while you were processing its request. For example, if the client asks you
    to add a comment to floot XYZ, but floot XYZ doesn't exist, you can return
    an "error 404" to indicate you couldn't find floot XYZ:

    return HTTPError(404, "Floot ID " + floot_id + " does not exist in the database")
    """
    def __init__(self, status, message):
        self.status = status
        self.message = message
