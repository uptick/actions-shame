# Shame Action

This action can be used to notify a slack channel on a failed test.

This action can also be used to notify a slack channel when a **CI JOB** passes.

On a `praise` command, the action will search your git history for the last completed JOB
matching the current job. If the last job was a failure, this action will praise the author for fixing it.

This Action is able to search users in your slack organisation and match the user with the most
similar name and email to the git commit author.

## Inputs

### `command`

**Required** The command to use. `shame` or `praise` dictates the type of message.

### `SLACK_TOKEN`

**Required** The slack token with permissions to post a chat message and to search users.

### `SLACK_CHANNEL`

**Required** The channel to notify.

### `GITHUB_TOKEN`

**Required** The `GITHUB_TOKEN` with permissions to `read:actions`.

## Example usage

```yaml
permissions:
  actions: read

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
        with:
          # TODO: Configure fetch-depth?
          fetch-depth: 2

      - name: Test shame works
        if: startsWith(env.BRANCH_NAME, 'main') && failure()
        id: shame
        uses: uptick/actions-shame@main
        with:
          command: "shame"
          SLACK_TOKEN: ${{ secrets.SLACK_TOKEN }}
          SLACK_CHANNEL: "devops-test-slack"
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Test praise works
        if: startsWith(env.BRANCH_NAME, 'main') && success()
        id: praise
        uses: uptick/actions-shame@main
        with:
          command: "praise"
          SLACK_TOKEN: ${{ secrets.SLACK_TOKEN }}
          SLACK_CHANNEL: "devops-test-slack"
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
