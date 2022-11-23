"""
Shame and praise.
"""
import argparse
import json
import os
import urllib.request

import get_slack_user
import uptick_github as github

SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "devops-test-slack")
SLACK_TOKEN = os.environ.get("SLACK_TOKEN", "")


class Slack:
    """Simple wrapper around the slack api"""

    # https://api.slack.com/apps/A02EUJFSS4D
    def __init__(self):
        self.token = os.environ.get("SLACK_TOKEN")
        self.base_url = "https://slack.com/api/"

    def get_commit_author(self) -> get_slack_user.SlackUser:
        return get_slack_user.main(
            get_slack_user.default_user, get_slack_user.default_email, SLACK_TOKEN
        )

    def post_message(
        self, text: str, channel: str = SLACK_CHANNEL, color: str = ""
    ) -> None:
        data = {
            "attachments": [
                {
                    "color": color,
                    "text": text,
                }
            ],
            "channel": channel,
            "icon_url": "https://uptick-ci-storage.onuptick.com/robotwombat.png",
        }
        data = json.dumps(data)
        data = data.encode()

        with urllib.request.urlopen(
            urllib.request.Request(
                f"{self.base_url}/chat.postMessage",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                data=data,
            )
        ) as response:
            data = json.loads(response.read())
            if data.get("ok") == False:
                raise Exception("API Error: ", data)
