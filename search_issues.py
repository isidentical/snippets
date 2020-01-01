import csv
from argparse import ArgumentParser
 
def filter_issues(query):
    with open("all_issues.csv") as issues:
        reader = csv.DictReader(issues)
        for row in reader:
            if row["status"] != '1':
                continue
            if query in row["title"].lower():
                yield row
def main():
    parser = ArgumentParser()
    parser.add_argument("query")
    namespace = parser.parse_args()
    issues = filter_issues(namespace.query)
    for issue in issues:
        print(f"bpo-{issue['id']}: {issue['title']} - https://bugs.python.org/issue{issue['id']}")

if __name__ == "__main__":
    main()
