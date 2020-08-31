class Response:
    """
    This class allows you to send a response to the client with a custom
    content_type.

    STUDENTS: You almost definitely won't need to use this.
    """
    def __init__(self, body, content_type="text/html"):
        self.body = body
        self.content_type = content_type

    def get_body(self):
        return self.body

    def get_body_bytes(self):
        if isinstance(self.body, (bytes, bytearray)):
            return self.body
        else:
            return bytes(str(self.body), "utf-8")

    def get_content_type(self):
        return self.content_type
