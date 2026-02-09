# Docker Disk Doctor

A safe, explain-first CLI tool that shows how Docker uses disk space and what is safe to clean.

## Why this exists
Blindly running `docker system prune` is stressful. Docker Disk Doctor explains what is using disk space before you remove anything.

## Features
- Disk usage breakdown
- Used vs unused detection
- Safe / unsafe labels
- Dry-run cleanup estimation

## Installation
```bash
pipx install git+https://github.com/AndreasRevdal/docker-disk-doctor.git
```

## Usage
```bash
docker-disk-doctor
```

## Safety
This tool **never deletes anything automatically**.

## Support
Built from real homelab pain.
If this helped you, buy me a compute ☕
https://buymeacoffee.com/revdal

## License
MIT
