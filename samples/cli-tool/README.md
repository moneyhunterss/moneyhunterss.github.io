# watchdir — File Watcher CLI

Watch a directory for new files matching a regex, run a command when they
appear. Like inotify + cron in one. Useful for:

- Auto-process uploaded CSVs → database
- Auto-resize uploaded images
- Auto-run tests on file change
- Auto-deploy on git push to bare repo
- Build pipelines without CI

## Quick start

```bash
# Watch ./input for new CSV files, run process.sh on each
python watchdir.py ./input '.*\.csv$' 'bash process.sh {}'

# Watch ./uploads for images, resize them
python watchdir.py ./uploads '(?i)\.(jpg|png)$' 'python resize.py {}'

# Watch for new SSH keys, run security scan
python watchdir.py ~/.ssh '.*\.pub$' 'ssh-keygen -lf {}'
```

## How it works

1. On start, scan directory + record all existing files as "seen"
2. Every `--interval` seconds (default 1.0), scan again
3. For each new file matching the regex pattern:
   - Add to "seen" set (won't trigger twice)
   - Run the command, substituting `{}` with the file path
4. Loop forever (Ctrl+C to stop)

## Use cases

### 1. CSV → database ingest
```bash
mkdir -p ingest
python watchdir.py ./ingest '.*\.csv$' 'python ingest.py --file {}'
# Drag CSVs into ./ingest/ — they get processed automatically
```

### 2. Image auto-resize
```bash
mkdir -p originals resized
python watchdir.py ./originals '(?i)\.(jpg|png|webp)$' \
    'magick {} -resize 800x800 ./resized/$(basename {})'
```

### 3. Auto-deploy on git push (bare repo)
```bash
mkdir -p /srv/repo.git
cd /srv/repo.git && git init --bare
python watchdir.py /srv/repo.git.git '.*' 'cd /var/www && git --git-dir={} pull'
```

### 4. Test auto-runner
```bash
python watchdir.py ./src '.*\.py$' 'pytest -x'
# Saves a file → tests auto-run
```

## Tech

- Python 3.10+
- `pathlib` — file system abstraction
- `concurrent.futures` — async polling
- Zero external dependencies (stdlib only)

## License

MIT — for your own automation pipelines.
