# Setup

This PR makes the project self-contained: `setup.sh` prepares everything and `run.sh` runs the scraper with a gentle configuration (1 thread, 30s wait) to avoid Google blocking.

## Local

```bash
./setup.sh   # venv + dependencies + Chrome hook (once)
./run.sh     # runs with queries.txt -> output/
./run.sh my_queries.txt my_output   # custom queries and output folder
```

- `setup.sh` looks for Chrome in: `~/chrome-for-testing/`, `~/.cache/puppeteer/`, `/usr/bin/`. If none is found, download Chrome for Testing to `~/chrome-for-testing/` and run again.
- The venv lives inside the project (`venv/`, gitignored).
- Chrome is linked via a `~/bin/google-chrome` symlink so the scraper finds it.

## Docker

```bash
docker build -t gmaps-scraper .
docker run --rm -v "$PWD/output:/app/output" gmaps-scraper -q queries.txt -o output
```
