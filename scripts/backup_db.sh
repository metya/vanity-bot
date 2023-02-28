cd /app
git add papers.db
git commit -m "backup papers.db" --no-verify
expect scripts/script.exp ${GITHUB_TOKEN}