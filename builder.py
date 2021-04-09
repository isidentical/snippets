#!/usr/bin/env python3


import logging
import os
import pwd
import shutil
import subprocess
import tempfile
import urllib
from argparse import ArgumentParser
from configparser import ConfigParser
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum, auto
from functools import partialmethod, wraps
from pathlib import Path

import apt

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(funcName)-15s --- %(message)s",
    datefmt="%m-%d %H:%M",
)


class Signal(Enum):
    UPDATE = auto()
    UPGRADE = auto()
    ABORTED = auto()
    DIST_UPGRADE = auto()


class BuildPath(Path):
    """A pathlib.Path subclass specialized for
    building a FS structure from scratch"""

    mkdir = partialmethod(Path.mkdir, parents=True, exist_ok=True)


@contextmanager
def prepare_environment(euid, home):
    def switch(euid, home):
        os.seteuid(euid)
        os.environ["HOME"] = home

    original_uid = os.getuid()
    original_home = os.fspath(Path("~").expanduser())
    try:
        switch(euid, home)
        yield
    finally:
        switch(original_uid, original_home)


@dataclass
class BuildCache:
    path: Path = Path("/opt/sysbuilder")

    @staticmethod
    def free(func):
        func.__cache_free__ = True
        return func

    def __post_init__(self):
        if self.path.exists():
            self.proxies = set(self.path.read_text().splitlines())
        else:
            self.proxies = set()

    def is_cached(self, proxy):
        cache_free = getattr(proxy, "__cache_free__", False)
        return proxy.__name__ in self.proxies and not cache_free

    def cache(self, proxy):
        self.proxies.add(proxy.__name__)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        with open(self.path, "w") as cache_f:
            cache_f.write("\n".join(self.proxies) + "\n")


def as_user(func):
    @wraps(func)
    def wrapper(options, cache):
        user = pwd.getpwnam(options.user)
        with prepare_environment(euid=user.pw_uid, home=user.pw_dir):
            return func(options, cache)

    return wrapper


def install(cache, *names):
    changes = len(names)
    for name in names:
        package = cache.get(name)
        if package is None:
            logging.warning(
                f"Can't install {name} since it doesn't enlisted in the cache"
            )
            continue

        if package.is_upgradable:
            package.mark_upgrade()
        elif package.is_installed:
            changes -= 1
            logging.debug(f"Package {name} already in the latest version")
        else:
            package.mark_install()
    if changes > 0:
        cache.commit()


def add_repo(cache, *repos):
    for repo in repos:
        subprocess.check_call(["add-apt-repository", "-y", repo])
    cache.open()


def snap_install(*args):
    subprocess.check_call(["snap", "install", *args])


def setup_sys(options, cache):
    install(
        cache,
        "apt-transport-https",
        "build-essential",
        "ca-certificates",
        "curl",
        "geany",
        "geany-plugins",
        "git",
        "gnupg-agent",
        "libbz2-dev",
        "libffi-dev",
        "liblzma-dev",
        "libncurses5-dev",
        "libncursesw5-dev",
        "libreadline-dev",
        "libsqlite3-dev",
        "libssl-dev",
        "llvm",
        "python-openssl",
        "software-properties-common",
        "tk-dev",
        "wget",
        "xz-utils",
        "zlib1g-dev",
    )


@as_user
def setup_ssh(options, cache):
    ssh_dir = Path(f"~/.ssh").expanduser()
    key_file = ssh_dir / "id_rsa"
    if key_file.exists():
        shutil.move(key_file, ssh_dir / "id_rsa.backup")

    keygen = ["ssh-keygen", "-q"]
    keygen.extend(["-f", key_file])
    keygen.extend(["-N", options.password])
    subprocess.check_call(keygen)
    logging.info("Sync SSH keys with GitHub && GCC compiler farm")


@as_user
def setup_git(options, cache):
    global_ignore = Path("~/.gitignore").expanduser()

    for key, value in (
        ("user.name", "Batuhan Taskaya"),
        ("user.email", "batuhanosmantaskaya@gmail.com"),
        ("core.excludesFile", global_ignore),
    ):
        subprocess.check_call(["git", "config", "--global", key, value])

    with open(global_ignore, "w") as ignore_f:
        for file in ("t.*", "t1.*"):
            ignore_f.write(file + "\n")


def install_firefox(options, cache):
    @as_user
    def configure_firefox(options, cache):
        firefox_base = Path("~/.mozilla/firefox/").expanduser()
        settings = {"browser.urlbar.placeholderName": "Google"}
        for preference_file in firefox_base.glob("**/prefs.js"):
            contents = preference_file.read_text().splitlines()
            for line_no, line in enumerate(contents.copy()):
                for key, value in settings.items():
                    if key in line:
                        contents[line_no] = f'user_pref("{key}", "{value}");'
            preference_file.write_text("\n".join(contents) + "\n")

    add_repo(cache, "ppa:ubuntu-mozilla-daily/firefox-aurora")
    install(cache, "firefox")
    configure_firefox(options, cache)


@as_user
def install_geany_extras(options, cache):
    geany_base = Path("~/.config/geany/").expanduser()
    geany_schemes = geany_base / "colorschemes"
    if geany_schemes.exists():
        shutil.rmtree(geany_schemes)

    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        subprocess.check_call(
            [
                "git",
                "clone",
                "https://github.com/geany/geany-themes",
                directory,
            ]
        )
        shutil.move(os.fspath(directory / "colorschemes"), geany_schemes)

    parser = ConfigParser()
    geany_conf = geany_base / "geany.config"
    if geany_conf.exists():
        parser.read(geany_conf)

    if "geany" not in parser.sections():
        parser.add_section("geany")

    parser["geany"]["indent_type"] = "0"
    parser["geany"]["pref_template_mail"] = "isidentical@gmail.com"
    with geany_conf.open("w") as conf_f:
        parser.write(conf_f)


def install_node_starter(options, cache):
    with tempfile.NamedTemporaryFile() as temp_file:
        file_name = temp_file.name
        urllib.request.urlretrieve(
            "https://deb.nodesource.com/setup_14.x", filename=file_name
        )
        subprocess.check_call(["bash", file_name])
    install(cache, "nodejs")


def install_utilities(options, cache):
    add_repo(cache, "ppa:atareao/telegram")

    install(cache, "telegram")
    install(cache, "vim-gtk3", "jq", "gdebi-core", "wget")
    with tempfile.NamedTemporaryFile() as temp_file:
        file_name = temp_file.name
        subprocess.check_call(
            [
                "wget",
                "-O",
                file_name,
                "https://discordapp.com/api/download?platform=linux&format=deb",
            ]
        )
        subprocess.check_call(["gdebi", "-n", file_name])
    snap_install("--beta", "authy")


def install_docker(options, cache):
    with tempfile.NamedTemporaryFile() as temp_file:
        file_name = temp_file.name
        urllib.request.urlretrieve(
            "https://download.docker.com/linux/ubuntu/gpg", filename=file_name
        )
        subprocess.check_call(["apt-key", "add", file_name])

    ubuntu_version = (
        subprocess.check_output(["lsb_release", "-cs"]).decode().strip()
    )
    add_repo(
        cache,
        f"deb [arch=amd64] https://download.docker.com/linux/ubuntu {ubuntu_version} stable",
    )
    install(
        cache, "docker-ce", "docker-ce-cli", "containerd.io", "docker-compose"
    )


def build(options):
    cache = apt.Cache()
    with BuildCache() as build_cache:
        for proxy in [
            setup_sys,
            setup_ssh,
            setup_git,
            install_docker,
            install_firefox,
            install_utilities,
            install_node_starter,
            install_geany_extras,
        ]:
            if build_cache.is_cached(proxy):
                continue

            signal = proxy(options, cache)
            build_cache.cache(proxy)
            if signal is None:
                continue
            elif signal is Signal.ABORTED:
                logging.debug(
                    f"Passing step '{proxy.__name__}' since requirements already satisfied."
                )
            elif signal is Signal.UPDATE:
                cache.update()
                cache.open()
            elif signal is Signal.UPGRADE:
                cache.upgrade()
            elif signal is Signal.DIST_UPGRADE:
                cache.upgrade(dist_upgrade=True)
            else:
                logger.error(
                    f"Proxy {proxy.__name__} returned an unknown signal of {signal}"
                )


def main():
    parser = ArgumentParser()
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    options = parser.parse_args()
    build(options)


if __name__ == "__main__":
    main()
