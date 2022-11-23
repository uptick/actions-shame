"""Helper script to extract the slack user_id from an email and a name.

Usage:
    python3 get_slack_user.py --name="William Chu" --email=test@uptickhq.com


Uses the jaccard similarity of pairwise characters of email/name/real_name to determine
the most similar user.

This script is written for python 3.8 compatibility (usage in github actions.)
"""
import argparse
import dataclasses
import json
import os
import subprocess
import urllib.request
from typing import Iterable, List, Tuple


@dataclasses.dataclass
class SlackUser:
    name: str
    email: str
    real_name: str
    id: str


def jaccard_similarity(x: Iterable, y: Iterable) -> float:
    """returns the jaccard similarity between two lists or strings"""
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality / float(union_cardinality)


def pairwise_tuples(x: str) -> List[Tuple[str, str]]:
    """Given William returns [(W,i), (i,l), (l,l), (l,i), (i,a), (a, m)]"""
    if not x or len(x) < 2:
        return [("", "")]
    else:
        return [(letter, x[i + 1]) for i, letter in enumerate(x[:-1])]


def search(name: str, email: str, users: List[SlackUser]) -> SlackUser:
    def scoring_fn(user: SlackUser) -> float:
        return (
            jaccard_similarity(pairwise_tuples(user.email), pairwise_tuples(email))
            + jaccard_similarity(pairwise_tuples(name), pairwise_tuples(user.name))
            + jaccard_similarity(pairwise_tuples(name), pairwise_tuples(user.real_name))
        )

    match = max(users, key=scoring_fn)
    return match


def main(name: str, email: str, token: str) -> SlackUser:

    with urllib.request.urlopen(
        urllib.request.Request(
            "https://slack.com/api/users.list?limit=300&pretty=1",
            headers={"Authorization": f"Bearer {token}"},
        )
    ) as response:
        data = json.loads(response.read())

    if not data["ok"]:
        raise Exception(data["error"])
    users = [
        SlackUser(
            m["name"].lower(),
            m["profile"].get("email", "").lower(),
            m.get("real_name", "").lower(),
            m["id"],
        )
        for m in data["members"]
        if not m["is_bot"]
    ]

    matched_user = search(name, email, users)
    print(matched_user.id)
    return matched_user


default_user = subprocess.check_output(
    "git log -n 1 --pretty=format:%an".split()
).decode("utf-8")
default_email = subprocess.check_output(
    "git log -n 1 --pretty=format:%ae".split()
).decode("utf-8")
parser = argparse.ArgumentParser(
    description=(
        "Extracts the slack user id the latest commit via text similarity against slack"
        " profiles"
    )
)
parser.add_argument(
    "--name",
    type=str,
    default=default_user,
    help="Full name of the user. Defaults to latest commit name.",
)
parser.add_argument(
    "--email",
    type=str,
    default=default_email,
    help="Email address of the user. Defaults to latest commit email.",
)
parser.add_argument(
    "--slack-token",
    type=str,
    default=os.environ.get("SLACK_TOKEN", ""),
    help="OAuth slack token. Defaults to environ SLACK_TOKEN",
)

if __name__ == "__main__":
    args = parser.parse_args()
    print("token=", os.environ.get("SLACK_TOKEN"))
    main(args.name, args.email, args.slack_token)
