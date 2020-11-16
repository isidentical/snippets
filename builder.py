#!/usr/bin/env python3


import os
import pwd
import apt
import urllib
import shutil
import logging
import tempfile
import subprocess
from argparse import ArgumentParser
from contextlib import contextmanager
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from functools import wraps, partialmethod
from enum import Enum, auto

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

def build(options):
    cache = apt.Cache()
    with BuildCache() as build_cache:
        for proxy in [
            setup_sys,
            setup_ssh,
            setup_git,
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
