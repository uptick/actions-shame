import datetime
import json
import logging
import os
import urllib.request
from functools import lru_cache
from typing import Literal

logger = logging.getLogger("github")
##
# A workflow has many jobs (frontend -> lint/tsc/etc)
# A run is a single run of a workflow
# We need the last status of a job of the previous failing run for a job
#

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_JOB_NAME = os.environ.get("GITHUB_JOB")
GITHUB_RUN_ID = os.environ.get("GITHUB_RUN_ID")
GIT_HASH = os.environ.get("GIT_SHORT_HASH")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")  # uptick/workforce
REF = os.environ.get("GITHUB_HEAD_REF")
GITHUB_JOB_LINK = f"https://github.com/{GITHUB_REPOSITORY}/actions/runs/{GITHUB_RUN_ID}"
GITHUB_COMMIT_LINK = f"https://github.com/{GITHUB_REPOSITORY}/commit/{GIT_HASH}"
BRANCH_NAME = os.environ.get("BRANCH_NAME")
REPO_LINK = f"https://github.com/{GITHUB_REPOSITORY}"


BASE_URL = "https://api.github.com"
DEBUG = os.environ.get("DEBUG")


def parse_github_time(s: str) -> datetime.datetime:
    try:
        return datetime.datetime.fromisoformat(s)
    except ValueError:
        try:
            d = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
            return d
        except ValueError:
            d = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
            return d


class Github:
    def get_headers(self):
        return {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Content-Type": "application/json",
        }

    def get(self, url: str) -> dict:
        if DEBUG:
            print(">>> FETCHING: ", url)
        url = f"{BASE_URL}{url}" if not url.startswith("https://") else url
        with urllib.request.urlopen(
            urllib.request.Request(
                url,
                headers=self.get_headers(),
            )
        ) as response:
            data = json.loads(response.read())
            if DEBUG:
                print(json.dumps(data, indent=2))
            return data

    @lru_cache
    def get_github_run(self) -> dict:
        run = self.get(f"/repos/{GITHUB_REPOSITORY}/actions/runs/{GITHUB_RUN_ID}")
        return run

    @lru_cache
    def get_github_job(self) -> dict:
        jobs_url = self.get_github_run()["jobs_url"]
        jobs = self.get(jobs_url)
        for job in jobs["jobs"]:
            # GITHUB_JOB is often the short hand name of the ci yaml
            # There is no way to uniquely identify a job that is consistent in githubs api.
            if GITHUB_JOB_NAME in job["name"]:
                return job

    def get_time_taken(self) -> str:
        job = self.get_github_job()
        # We are still running at this point
        seconds_taken = (
            datetime.datetime.utcnow()
            - parse_github_time(job["steps"][0]["started_at"])
        ).total_seconds()

        # 2022-11-23T21:17:19.000Z

        minutes = int(seconds_taken // 60)
        seconds = int(seconds_taken % 60)
        return f"{minutes}m {seconds}s"

    @lru_cache
    def get_workflow_id(self) -> int:
        return self.get_github_run()["workflow_id"]

    def get_previous_build_status(self) -> Literal["success", "failure"]:
        """We need the previous build status of the job of the **SAME** branch
        https://docs.github.com/en/rest/actions/workflows
        """
        completed = self.get(
            f"/repos/{GITHUB_REPOSITORY}/actions/workflows/{self.get_workflow_id()}/runs?per_page=1&status=completed&branch={BRANCH_NAME}"
        )
        partial = self.get(
            f"/repos/{GITHUB_REPOSITORY}/actions/workflows/{self.get_workflow_id()}/runs?per_page=1&status=partial&branch={BRANCH_NAME}"
        )

        completions = []
        for response in (completed, partial):
            if response["workflow_runs"]:
                latest_completed = completed["workflow_runs"][0]
                latest_completed_jobs = self.get(latest_completed["jobs_url"])
                for job in latest_completed_jobs["jobs"]:
                    # GITHUB_JOB is often the short hand name of the ci yaml
                    # There is no way to uniquely identify a job that is consistent in githubs api.
                    if job["status"] == "completed" and GITHUB_JOB_NAME in job["name"]:
                        conclusion = job["conclusion"]
                        completed_at = parse_github_time(
                            job["steps"][-1]["completed_at"]
                        )
                        completions.append((completed_at, conclusion))

        if completions:
            latest_completion = max(completions)
            print(
                f"Latest completion for: branch={BRANCH_NAME} job={GITHUB_JOB_NAME} is {latest_completion[1]}. Completed at {latest_completion[0]}"
            )
            return latest_completion[1]
        return "success"


if __name__ == "__main__":
    GITHUB_RUN_ID = "3529530709"
    GITHUB_REPOSITORY = "uptick/actions"
    BRANCH_NAME = "release/slack-error"
    GITHUB_JOB_NAME = "ci"

    gh = Github()
    print(gh.get_github_job())
    print(gh.get_time_taken())
