# Copyright 2024 tison <wander4096@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import dateparser
from githubkit import GitHub
from githubkit.versions.latest.models import Issue


def unassign(token, owner, repo, period, dryrun):
    c = GitHub(token)
    dt = dateparser.parse(period, settings={'RETURN_AS_TIMEZONE_AWARE': True})
    print(f'[{owner}/{repo}] Open issues updated before {dt} ({period}) will be considered stale.')

    for issue in c.paginate(
        c.rest.issues.list_for_repo,
        owner=owner,
        repo=repo,
        state='open',
        sort='updated',
        direction='asc'
    ):
        issue: Issue

        assignees = set()
        if issue.assignees is not None:
            assignees = assignees.union({ assignee.login for assignee in issue.assignees })
        if issue.assignee is not None:
            assignees.add(issue.assignee.login)

        if len(assignees) > 0 and issue.updated_at < dt:
            print(f'[{owner}/{repo}] Issue {issue.number} is stale, last updated at {issue.updated_at}. Assignees: {assignees}')
            if dryrun:
                print(f'[{owner}/{repo}] Dryrun mode, issue {issue.number} would be unassigned.')
            else:
                c.rest.issues.remove_assignees(
                    owner=owner,
                    repo=repo,
                    issue_number=issue.number,
                    assignees=list(assignees))
                print(f'[{owner}/{repo}] Assignees {assignees} of issue {issue.number} is unassigned.')


def main():
    parser = argparse.ArgumentParser(description='Auto unassign stale issues')
    parser.add_argument('--token', help='GitHub token')
    parser.add_argument('--repo', help='Repository name', required=True)
    parser.add_argument('--period', help='Period to consider stale', default='14 days ago')
    parser.add_argument('--dryrun', help='Dryrun mode', action='store_true')
    args = parser.parse_args()
    owner, repo = args.repo.split('/')
    unassign(args.token, owner, repo, args.period, args.dryrun)
