import uptick_github as github
import uptick_slack as slack

gh_client = github.Github()
slack_client = slack.Slack()
additional_text = ""

if __name__ == "__main__":
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
