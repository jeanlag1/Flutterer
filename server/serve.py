#! /usr/bin/env python3

"""
This contains a tiny implementation of a flexible web server.

STUDENTS: You're welcome to look around this file if you're interested, but you
don't need to, and you certainly don't need to modify anything here.
"""

import json
import re
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

import api
from colorama import Fore, Style, init
from error import HTTPError
from response import Response

SERVER_PORT = 1066

def flutterer_print(*args, **kwargs):
    timestamp = time.strftime("%I:%M:%S %p").lower()
    print(f"{Fore.LIGHTBLACK_EX}{timestamp}{Style.RESET_ALL} {Fore.LIGHTBLUE_EX}[Flutterer]{Style.RESET_ALL}",
          *args, Style.RESET_ALL, **kwargs)


def print_gray(msg):
    flutterer_print(f"{Fore.LIGHTBLACK_EX}{Style.BRIGHT}{msg}{Style.RESET_ALL}")

def print_green(msg):
    flutterer_print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")

def print_red(msg):
    flutterer_print(f"{Fore.RED}{msg}{Style.RESET_ALL}")

def find_route(path, route_list):
    for route in route_list:
        criteria = route[0]
        handler = route[1]
        if isinstance(criteria, str):
            if path == criteria:
                # Route takes no args, so return empty args dict
                return (handler, {})
        elif isinstance(criteria, tuple):
            if re.fullmatch("^" + criteria[0] + "$", path):
                arg_names = criteria[1:]
                match = re.findall("^" + criteria[0] + "$", path)[0]
                match_components = match if isinstance(match, tuple) else (match,)
                return (handler, dict(zip(arg_names, match_components)))
        else:
            raise TypeError(f"route[0] has unknown type: {route}")

class FluttererHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self._http_error = None
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def _log_request_start(self):
        # Print the first half of the log message, so students can see what the
        # request was if they print some debugging messages
        print_gray(f"{self.command} {self.path}")

    def log_request(self, code=None, size=None):
        # Print the second half of the log message (response info)
        msg = f"  -> {code} {self.responses[code][0]}"
        if self._http_error:
            msg += f": {self._http_error.message}"
            self._http_error = None
        (print_green if code == 200 else print_red)(msg)

    def _service_request(self, routes, extra_params=None):
        try:
            route_match = find_route(self.path, routes)
            if not route_match:
                raise HTTPError(404, "Matching route not found")
            handler, args = route_match
            if extra_params:
                args.update(extra_params)
            output = handler(**args)
            self._send_reponse(handler, output)
        except HTTPError as e:
            self._handle_http_error(e)
        except Exception:
            self._handle_internal_server_error()
            raise

    def _send_reponse(self, handler_function, output):
        # These are the acceptable output types:
        #
        # * string (gets returned as plain text)
        # * list or dict (gets serialized to JSON)
        # * Response (gets written out with appropriate content type)
        # * HTTPError (gets thrown as an exception, which is subsequently
        #   caught and written as an error with appropriate status code)
        #
        # Anything else indicates the student is probably not doing what they
        # meant to do, so we throw an exception.
        if isinstance(output, str):
            output = Response(output, content_type="text/plain")
        elif isinstance(output, list) or isinstance(output, dict):
            output = Response(json.dumps(output, indent=4),
                              content_type="application/json")
        elif isinstance(output, Response):
            # nothing to do here
            pass
        elif isinstance(output, HTTPError):
            raise output
        else:
            raise TypeError(f"Function {handler_function.__name__!r} returned unacceptable "
                    f"output: {output!r}\n"
                    "Your function should return one of these:\n"
                    " * A string (to be sent to the client as plain text)\n"
                    " * A list or dictionary (to be sent to the client as JSON)\n"
                    " * A Response object (if you are trying to send a specific content-type)\n"
                    " * An HTTPError (if you want to report an error to the client)")

        self.send_response(200)
        self.send_header("Content-Type", output.get_content_type())
        self.end_headers()
        self.wfile.write(output.get_body_bytes())

    def _handle_internal_server_error(self):
        self.send_response(500)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(f"Unexpected server error (see terminal for details)",
                                "utf-8"))

    def _handle_http_error(self, e):
        self._http_error = e
        self.send_response(e.status)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(f"Error: {e.message}", "utf-8"))

    def do_GET(self):
        self._log_request_start()
        self._service_request(api.GET_ROUTES)

    # Handles POST requests
    def do_POST(self):
        self._log_request_start()

        ctype = self.headers["Content-Type"]

        # refuse to receive non-json content
        if ctype != "application/json":
            self._handle_http_error(HTTPError(400,
                    "Error in serve.py: Expected the client to specify a content "
                    f"type of 'application/json', but got {ctype!r} instead."))
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers["Content-Length"])
        try:
            info = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            self._handle_http_error(HTTPError(400,
                    "Error in serve.py: The request body received from the client "
                    "is not valid JSON."))
            return

        self._service_request(api.POST_ROUTES, {
            "request_body": info,
        })

if __name__ == "__main__":
    init()  # initialize terminal color support
    server = HTTPServer(("0.0.0.0", SERVER_PORT), FluttererHandler)
    flutterer_print(f"Listening for requests at http://localhost:{SERVER_PORT}")
    server.serve_forever()
