import sys
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

directory = Path(sys.argv[1])
output_directory = directory / 'out'
output_directory.mkdir(exist_ok=True)

def add_subtitle(mkv_file):
    if not (sub_file := mkv_file.with_suffix('.en.srt')).exists():
        print(f"subtitle couldn't found for {mkv_file!s}, skipping")
        return None

    dest_file = output_directory / mkv_file.name
    subprocess.check_call([
        'ffmpeg',
        '-i',
        str(mkv_file),
        '-vf',
        repr(f'subtitles={sub_file!s}'),
        str(dest_file)
    ])
    return mkv_file

with ProcessPoolExecutor(max_workers=4) as executor:
    mkv_files = tuple(directory.glob('*.mkv'))
    for n, mkv_file in enumerate(executor.map(add_subtitle, mkv_files)):
        if mkv_file is not None:
            print(f'{n}/{len(mkv_files)} => {mkv_file}')
