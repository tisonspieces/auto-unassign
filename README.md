# GitHub Actions Auto Unassign

Auto unassign issues if stale:

```yaml
name: Auto Unassign
on:
  schedule:
    - cron: '4 2 * * *'

permissions:
  contents: read
  issues: write
  pull-requests: write

jobs:
  auto-unassign:
    name: Auto Unassign
    runs-on: ubuntu-latest
    steps:
      - name: Auto Unassign
        uses: tisonspieces/auto-unassign@main
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          repository: ${{ github.repository }}
          period: '14 days ago'
```

You can find the supported period pattern in [dateparser](https://dateparser.readthedocs.io/en/latest/index.html).
