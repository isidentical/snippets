import sys
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

directory = Path(sys.argv[1])
output_directory = Path("/home/isidentical/disk/plex/TV Shows/")
output_directory.mkdir(exist_ok=True, parents=True)

for video_file in directory.glob("*.mkv"):
    srt_file = video_file.with_suffix(".srt")

    show_name, metadata, title = video_file.name.split(" - ")
    season, episode = metadata.strip('[]').split('x')

    season = season.zfill(2)
    episode = episode.zfill(2)

    base_video_file = (output_directory / show_name)
    base_video_file /= f'Season {season.zfill(2)}'
    base_video_file.mkdir(exist_ok=True, parents=True)

    base_video_file /= f'{show_name}-s{season}e{episode}'
    
    video_output_file = base_video_file.with_suffix(video_file.suffix)
    srt_output_file = base_video_file.with_suffix('.en' + srt_file.suffix)
    
    subprocess.check_call(['cp', video_file, video_output_file])
    subprocess.check_call(['cp', srt_file, srt_output_file])
    
