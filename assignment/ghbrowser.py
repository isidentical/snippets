import argparse
import json
import logging
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from string import Template
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

logging.basicConfig(level=logging.DEBUG)

CLIENT_ID = os.getenv("GH_BASIC_CLIENT_ID")
CLIENT_SECRET = os.getenv("GH_BASIC_SECRET_ID")
TEMPLATE_BASE = Path(__file__).parent / "static"

if not (CLIENT_ID and CLIENT_SECRET):
    logging.error(
        "Couldn't locate client_id & client_secret_id inside of environ vars!"
    )
    exit(1)


def get_template(path):
    template = (TEMPLATE_BASE / f"{path}.tmpl").read_text()
    template = Template(template)
    return template


def send_github_request(endpoint, method="get", **body):
    request = Request(endpoint)
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")

    if method == "post":
        page = urlopen(request, json.dumps(body).encode("UTF-8"))
    elif method == "get":
        request.full_url += "?" + urlencode(body)
        page = urlopen(request)
    else:
        raise ValueError(f"Invalid method, {method}")

    with page as result:
        response = json.loads(result.read().decode())

    return response


class GHBrowser(BaseHTTPRequestHandler):
    _handlers = {}

    @classmethod
    def register(cls, path):
        def wrapper(func):
            cls._handlers[path] = func
            return func

        return wrapper

    def do_GET(self):
        path = self.path.split("/")
        path = "/".join(path[:2])
        if path in self._handlers:
            return self._handlers[path](self)
        else:
            return self.send_notfound()

    def send_notfound(self):
        self.send_error(HTTPStatus.NOT_FOUND, "Path not found")

    def send_html_response(self, code, html):
        content = html.encode("UTF-8", "replace")
        self.send_response(code)
        self.send_header("Content-Type", "text/html;charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


@GHBrowser.register("/")
def home(request):
    template = get_template("index")
    content = template.substitute(client_id=CLIENT_ID)
    return request.send_html_response(HTTPStatus.OK, content)


@GHBrowser.register("/login")
def login(request):
    query = urlparse(request.path).query
    query = parse_qs(query)

    if "code" not in query:
        return self.send_notfound()
    (code,) = query["code"]

    access_token = send_github_request(
        "https://github.com/login/oauth/access_token",
        method="post",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        code=code,
    )

    if "access_token" not in access_token:
        return request.send_html_response(
            HTTPStatus.UNAUTHORIZED, "<h1>Expired Code</h1>"
        )

    access_token = access_token["access_token"]
    user = send_github_request(
        "https://api.github.com/user", access_token=access_token
    )
    repos = send_github_request(user["repos_url"], access_token=access_token)
    list_template = "\n".join(
        get_template("list").substitute(**repo) for repo in repos
    )

    template = get_template("final")
    content = template.substitute(
        avatar_url=user["avatar_url"],
        name=user["login"],
        list_template=list_template,
    )
    return request.send_html_response(HTTPStatus.OK, content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-H", "--host", help="Server host", default="0.0.0.0", type=str
    )
    parser.add_argument(
        "-P", "--port", help="Server port", default=8000, type=int
    )

    args = parser.parse_args()
    connection = (args.host, args.port)
    with HTTPServer(connection, GHBrowser) as httpd:
        logging.info("Starting server at %s:%s", *httpd.server_address)
        httpd.serve_forever()
