#!/usr/bin/env python

import imdb
from concurrent.futures import ThreadPoolExecutor, as_completed
from argparse import ArgumentParser
from functools import partial
from difflib import SequenceMatcher

IA = imdb.IMDb()


def _title_sorter(query, title):
    matcher = SequenceMatcher(a=query, b=title.get("title") or "")
    return matcher.ratio(), title.get("kind") == "tv series"


def title_to_id(query):
    titles = IA.search_movie(query)
    if len(titles) == 0:
        raise ValueError("No match for: " + query)

    titles.sort(key=partial(_title_sorter, query))
    titles.reverse()
    for n, title in enumerate(titles):
        if name := title.get("title"):
            print(f"{n}.", name, f"({title.get('year', 'unknown')})")

    index = int(input(">>> "))
    return titles[index].movieID


def get_birth_place(cast):
    IA.update(cast, ["main"])
    return cast.get("birth info", {}).get("birth place") or ""


def _imdb_search_country_in_cast(movie_id, search_text):
    movie = IA.get_movie(movie_id)
    IA.update(movie, "full credits")

    cast = movie["cast"]

    print(f"{movie['title']} ({movie['year']})\n")
    print(f"Searching through {len(cast)}")

    search_text = search_text.casefold()
    final_results = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        cast_futures = {
            executor.submit(get_birth_place, cast): cast for cast in cast
        }
        for progress, future in enumerate(as_completed(cast_futures.keys())):
            if progress % 20 == 0:
                print(f"Progress: {progress}/{len(cast)}", end="\r")

            actor, birth_place = cast_futures[future], future.result()
            if search_text in birth_place.casefold():
                text = f"{actor['name']} ({birth_place})"
                print("=====> ", text)
                final_results.append(text)
    print("\n\n\n")
    print("Found: ")
    print(*final_results, sep="\n")


def main():
    parser = ArgumentParser()
    parser.add_argument("title")
    parser.add_argument("query")
    options = parser.parse_args()
    possible_id = title_to_id(options.title)
    _imdb_search_country_in_cast(possible_id, options.query)


if __name__ == "__main__":
    main()
