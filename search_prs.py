import csv
from argparse import ArgumentParser


def filter_prs(query):
    with open("prs.csv") as prs:
        reader = csv.DictReader(prs)
        for row in reader:
            if row["State"] != "open":
                continue
            if query in row["Title"].lower():
                yield row


def main():
    parser = ArgumentParser()
    parser.add_argument("query")
    namespace = parser.parse_args()
    pull_requests = filter_prs(namespace.query)

    for pull_request in pull_requests:
        print(
            f"#{pull_request['#']} - {pull_request['Title']} (by {pull_request['User']}) {pull_request['URL']}"
        )


if __name__ == "__main__":
    main()
