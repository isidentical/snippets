import json
import time
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request

BASE = "https://buildbot.python.org/all/api/v2"
CONFIG_PATH = Path("~/.buildbots.json").expanduser()
STATE_REPR = {
    0: "✔",
    1: "⚠️",
    2: "❌",
}


def make_request(request):
    with urlopen(request) as page:
        return json.load(page)


def refresh_ids(config):
    builders = {builder["name"]: builder for builder in config["builders"]}
    all_builders = make_request(BASE + "/builders")["builders"]

    for builder in all_builders:
        if builder["name"] in builders:
            builders[builder["name"]]["id"] = builder["builderid"]

    dump_config(config)


def get_builds(**kwargs):
    request = Request(BASE + "/builds?" + urlencode(kwargs))
    return make_request(request)["builds"]


def dump_config(config):
    with CONFIG_PATH.open("w") as f:
        json.dump(config, f)


def read_config():
    with CONFIG_PATH.open() as config:
        return json.load(config)


def main():
    parser = ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--refresh-ids", action="store_true")
    options = parser.parse_args()

    if options.refresh_ids:
        refresh_ids(read_config())

    config = read_config()

    if options.force or CONFIG_PATH.stat().st_mtime + 60 * 60 * 24 < time.time():
        states = defaultdict(list)
        for builder in config["builders"]:
            for build in get_builds(
                builderid=builder["id"], limit=options.limit, order="-started_at"
            ):
                states[builder["name"]].append(
                    STATE_REPR.get(build["results"], "🔵")
                )
        config["states"] = dict(states)
        dump_config(config)

    for builder, builds in config["states"].items():
        print(builder, "===>", " ".join(builds))


if __name__ == "__main__":
    main()
