import os
import shelve
import sys
from pathlib import Path

DB_PATH = Path("~/.cache/backlog").expanduser()
DB_PATH.mkdir(exist_ok=True)


def initalize_if_needed(db):
    db.setdefault("backlog", [])


def backlog(command="list", parameter=None):
    with shelve.open(os.fspath(DB_PATH / "backlog.db"), writeback=True) as db:
        initalize_if_needed(db)

        if command == "peek":
            if len(db["backlog"]) == 0:
                print("Backlog cleared! Finally...")
            else:
                print(db["backlog"][0])
        elif command == "push" and parameter is not None:
            db["backlog"].append(parameter)
        elif command == "pop":
            if len(db["backlog"]) == 0:
                print("Nothing to pop!")
            else:
                item = db["backlog"].pop(0)
                print(item)
        elif command == "list":
            print(len(db["backlog"]), "task awaiting")
            for index, item in enumerate(db["backlog"]):
                print(index, "===>", item)
        elif command == "alter" and parameter is not None:
            item = db["backlog"].pop(int(parameter))
            print(item)
        else:
            print("Unknown command!")


if __name__ == "__main__":
    backlog(*sys.argv[1:])

# backlog
# > agenda item 1
# > agenda item 2
# backlog push "agenda item 3"
# backlog peek
# > agenda item 1
# backlog pop
# > agenda item 1
# backlog
# > agenda item 2
# > agenda item 3
