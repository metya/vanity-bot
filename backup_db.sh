#!/usr/bin/expect
cd /app
git add papers.db
git commit -m "backup papers.db" --no-verify
./script.exp ${GITHUB_TOKEN}