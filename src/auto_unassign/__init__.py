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
import datetime
import dateparser
from githubkit import GitHub
from githubkit.versions.latest.models import Issue


def unassign(token, owner, repo, period, dryrun):
    c = GitHub(token)
    dt = dateparser.parse(period, settings={'RETURN_AS_TIMEZONE_AWARE': True})
    print(f'[{owner}/{repo}] Open issues updated before {dt} ({period}) will be considered stale.')
    if dt > datetime.datetime.now(datetime.timezone.utc):
        print(f'[{owner}/{repo}] The period is in the future, no issue will be considered stale.')
        return

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
            if not dryrun:
                c.rest.issues.remove_assignees(
                    owner=owner,
                    repo=repo,
                    issue_number=issue.number,
                    assignees=list(assignees))
                print(f'[{owner}/{repo}] Assignees {assignees} of issue {issue.number} is unassigned.')


def strtobool(val):
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def main():
    parser = argparse.ArgumentParser(description='Auto unassign stale issues')
    parser.add_argument('--token', help='GitHub token')
    parser.add_argument('--repo', help='Repository name', required=True)
    parser.add_argument('--period', help='Period to consider stale', default='14 days ago')
    parser.add_argument('--dryrun', help='Dryrun mode', default=False, type=strtobool)
    args = parser.parse_args()
    owner, repo = args.repo.split('/')
    unassign(args.token, owner, repo, args.period, args.dryrun)
