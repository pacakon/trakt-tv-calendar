name: Build Calendar

on:
  workflow_dispatch:
  schedule:
    - cron: "0 5 * * *"

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests pytz

      - name: Refresh Trakt token (use refresh_token first)
        run: |
          echo "Running token_manager.py to refresh token..."
          python token_manager.py --no-device-flow

      - name: Build calendar
        run: |
          echo "Running build_calendar.py..."
          python build_calendar.py

      - name: Commit updated token_state.json
        run: |
          git config --global user.name "github-actions"
          git config --global user.email "github-actions@github.com"
          git add token_state.json
          git commit -m "Update token_state.json" || echo "No changes to commit"
          git push
