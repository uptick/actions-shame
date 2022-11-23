import argparse

import uptick_github as github
import uptick_slack as slack

gh_client = github.Github()
slack_client = slack.Slack()
additional_text = ""


parser = argparse.ArgumentParser(
    description=(
        "Extracts the slack user id the latest commit via text similarity against slack"
        " profiles"
    )
)
parser.add_argument(
    "command",
    choices=["shame", "praise"],
    type=str,
)


def praise():
    # https://api.slack.com/methods/chat.postMessage
    author = slack_client.get_commit_author()
    context = {
        "job_link": f"<{gh_client.get_github_job()['html_url']}|job:{github.GITHUB_JOB_NAME}>",
        "hash_link": f"<{github.GITHUB_COMMIT_LINK}|({github.GIT_HASH})>",
        "repo_link": f"<{github.REPO_LINK}|repo:{github.GITHUB_REPOSITORY}>",
        "ref": f"{github.REF}",
        "time_msg": f"in {gh_client.get_time_taken()}",
        "name": f"<@{author.id}>",
        "additional_text": additional_text,
        "branch_name": github.BRANCH_NAME,
    }
    text = """
:raised_hands: *BUILD FIXED!* Great work {name} :raised_hands:
{repo_link} | {branch_name} | {job_link} | Success | {hash_link} {time_msg}
{additional_text}
""".format(
        **context
    )

    if gh_client.get_previous_build_status() == "failure":
        slack_client.post_message(
            text=text,
            channel=slack.SLACK_CHANNEL,
            color="good",
        )


def shame():
    # https://api.slack.com/methods/chat.postMessage
    author = slack_client.get_commit_author()

    context = {
        "job_link": f"<{gh_client.get_github_job()['html_url']}|job:{github.GITHUB_JOB_NAME}>",
        "hash_link": f"<{github.GITHUB_COMMIT_LINK}|({github.GIT_HASH})>",
        "repo_link": f"<{github.REPO_LINK}|repo:{github.GITHUB_REPOSITORY}>",
        "ref": f"{github.REF}",
        "time_msg": f"in {gh_client.get_time_taken()}",
        "name": f"<@{author.id}>",
        "additional_text": additional_text,
        "branch_name": github.BRANCH_NAME,
    }
    text = """
:poop: *SHAME!* {name} *SHAME!* :poop:
{repo_link} | {branch_name} | {job_link} | Failure | {hash_link} {time_msg}
{additional_text}
""".format(
        **context
    )

    slack_client.post_message(
        text=text,
        channel=slack.SLACK_CHANNEL,
        color="#ff4d4d",
    )


if __name__ == "__main__":
    args = parser.parse_args()
    if args.command == "shame":
        shame()
    else:
        praise()
