import os
import shelve
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from pprint import pprint
from typing import Any, Dict, List, Optional
from urllib.request import urlopen

TOTAL_PAGES = 16
CACHE_PATH = Path("~/.local/url.db").expanduser()
UNI_URL_FORMAT = "https://wiz.pwr.edu.pl"
PAPER_INDEX_RE = re.compile(
    r"https:\/\/dona\.pwr\.edu\.pl\/s" r"zukaj\/default\.aspx\?nrewid=\d+"
)


def request(url, db_path=os.fspath(CACHE_PATH)):
    db = shelve.open(db_path)
    if url not in db:
        with urlopen(url) as page:
            db[url] = page.read().decode()
        db.sync()
    return db[url]


@dataclass
class Employee:
    name: str
    details: str
    paper_index: Optional[str] = None


class EmployeeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.employees = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("class") == "title":
            employee = Employee(name=attrs["title"], details=attrs["href"])
            self.employees.append(employee)


parser = EmployeeParser()
for page in range(1, TOTAL_PAGES + 1):
    print(f"Crawling page {page}...")
    source = request(UNI_URL_FORMAT + f"/en/employees/page{page}.html")
    parser.feed(source)

for employee in parser.employees:
    print(f"Parsing {employee.name}")
    source = request(UNI_URL_FORMAT + employee.details)
    if match := PAPER_INDEX_RE.search(source):
        employee.paper_index = match.group(0)

for employee in parser.employees:
    if employee.paper_index is not None:
        print(employee.name, UNI_URL_FORMAT + employee.details)
        import webbrowser

        webbrowser.open(UNI_URL_FORMAT + employee.details)
