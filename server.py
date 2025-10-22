#!/usr/bin/env python3
"""
A minimal HTTP server that serves files from the current working directory
or returns a simple greeting for unknown paths.

Usage:
    python server.py [--port PORT] [--host HOST]

The server uses the standard library's http.server module and runs in a
single thread. It is intended for quick testing or local development.
"""

import argparse
import logging
import os
import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Threaded HTTP server
# --------------------------------------------------------------------------- #
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


# --------------------------------------------------------------------------- #
# Custom request handler
# --------------------------------------------------------------------------- #
class CustomHandler(SimpleHTTPRequestHandler):
    """Serve files from the current directory or a greeting."""

    def do_GET(self):
        """Serve a GET request."""
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<html><head><title>Simple HTTP Server</title></head>"
                b"<body><h1>Hello, world!</h1>"
                b"<p>Serving files from: "
                + os.path.abspath(".").encode("utf-8")
                + b"</p></body></html>"
            )
        else:
            # Delegate to the base class for file serving
            super().do_GET()

    def log_message(self, format, *args):
        """Override to use the logging module instead of printing to stderr."""
        logger.info("%s - - [%s] %s",
                    self.client_address[0],
                    self.log_date_time_string(),
                    format % args)


# --------------------------------------------------------------------------- #
# Argument parsing
# --------------------------------------------------------------------------- #
def parse_args():
    parser = argparse.ArgumentParser(description="Run a simple HTTP server.")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Hostname to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number to listen on (default: 8000)",
    )
    parser.add_argument(
        "--directory",
        default=os.getcwd(),
        help="Directory to serve files from (default: current working directory)",
    )
    return parser.parse_args()


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #
def main():
    args = parse_args()

    # Change working directory if a custom directory is requested
    if os.path.isdir(args.directory):
        os.chdir(args.directory)
        logger.info("Serving files from: %s", os.path.abspath(args.directory))
    else:
        logger.error("Directory does not exist: %s", args.directory)
        sys.exit(1)

    server_address = (args.host, args.port)
    httpd = ThreadedHTTPServer(server_address, CustomHandler)

    try:
        logger.info("Starting server at http://%s:%d", args.host, args.port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server.")
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    main()