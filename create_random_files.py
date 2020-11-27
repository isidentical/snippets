import sys
import secrets
from pathlib import Path

files = Path(sys.argv[1])
files.mkdir(exist_ok=True)
for _ in range(int(sys.argv[2])):
    new_path = files / (str(_) + ".txt")
    with open(new_path, "w") as f:
        f.write(sys.argv[1][-1] + str(_))

