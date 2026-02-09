# Docker Disk Doctor

Docker Disk Doctor is a safe, explain-first CLI tool that shows **how Docker is using disk space** and what is **safe to clean** — without blindly running `docker system prune`.

Built from real homelab and infrastructure pain.

---

## Why this exists

Docker is great… until your disk suddenly fills up.

At that point, most people run:

```bash
docker system prune -a
```

…and *hope for the best*.

Docker Disk Doctor exists to answer one simple question **before you delete anything**:

> *What exactly is using my disk space, and what is safe to remove?*

This tool **does not delete anything automatically**.  
It explains first, so you can decide.

---

## Features

- Breakdown of Docker disk usage:
  - Images (used vs unused)
  - Containers (running vs stopped)
  - Volumes (attached vs orphaned)
- Clear, readable CLI output
- Designed for homelabs, servers, and real systems

---

## Installation

### Prerequisites

You need `pipx` installed.

On most Debian/Ubuntu-based systems:

```bash
sudo apt update
sudo apt install -y pipx
pipx ensurepath
```

You may need to open a **new shell** after running `pipx ensurepath`.

---

### Install Docker Disk Doctor

Install directly from GitHub:

```bash
pipx install git+https://github.com/AndreasRevdal/docker-disk-doctor.git
```

This installs the `docker-disk-doctor` command globally for your user.

> Note: This project is currently installed directly from GitHub.  
> A PyPI release (`pipx install docker-disk-doctor`) will come later.

---

## Usage

```bash
docker-disk-doctor
```

---

## Safety

Docker Disk Doctor **never deletes anything automatically**.

No prune.  
No cleanup without confirmation.  
No surprises.

---

## Support

If this tool saved you time, stress, or disk space,  
consider buying me a compute ☕  

https://buymeacoffee.com/revdal

---

## License

MIT License