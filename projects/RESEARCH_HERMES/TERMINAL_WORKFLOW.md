# Terminal Workspace Guide for RESEARCH_HERMES

## Honest status check

**`tmux` is not available in the current shell.** The environment is MSYS2/Git Bash on Windows 11, and neither `tmux` nor `pacman` are installed. Native Windows does not run tmux.

You have **three practical paths** to multi-session efficiency:

| Path | Effort | Best for |
|------|--------|----------|
| **Windows Terminal panes** (already installed) | 1 minute | Immediate work on this project |
| **WSL2 + tmux** | 15–30 minutes | Real tmux workflow; long-term |
| **MSYS2 proper with `pacman install tmux`** | 10–20 minutes | tmux inside the same Git Bash style shell |

The fastest win is **Windows Terminal panes** — already installed and closer to tmux than you'd expect.

---

## Option 1: Windows Terminal panes (use this now)

### Launch the project workspace

The environment is Git Bash on Windows 11, and Windows Terminal is already installed. The reliable launchers are:

- **PowerShell launcher (recommended):**
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\point\projects\RESEARCH_HERMES\launch_workspace.ps1"
  ```

- **Batch launcher (double-click, or run from cmd):**
  ```cmd
  C:\Users\point\projects\RESEARCH_HERMES\launch_workspace.cmd
  ```

It opens **three panes**:
1. **Left tall pane** — project root (`RESEARCH_HERMES`) for git, memory, top-level commands.
2. **Top-right** — `aqra/` directory for tests, pipeline, and code edits.
3. **Bottom-right** — `docs/superpowers/specs/` for paper and moonshot specs.

### Essential shortcuts

| Action | Shortcut |
|--------|----------|
| New tab | `Ctrl+Shift+T` |
| Close pane | `Ctrl+Shift+W` |
| Split vertical | `Alt+Shift++` |
| Split horizontal | `Alt+Shift+-` |
| Move focus | `Alt+Arrow` |
| Resize pane | `Alt+Shift+Arrow` |
| Zoom pane | `Ctrl+Shift+Z` (toggle) |
| Switch tab | `Ctrl+Tab` / `Ctrl+Shift+Tab` |
| Rename tab | Right-click tab |

### Suggested tabs for this project

| Tab name | Purpose |
|----------|---------|
| `main` | Project root — git status, memory edits, top-level commands |
| `aqra` | `cd aqra` — `uv run pytest`, `make paper`, pipeline runs |
| `paper` | `aqra/docs/paper` + `docs/superpowers/specs` — edit draft, specs |
| `logs` | Tail live monitor logs / memory files |
| `math` | `prometheus-math/` — C₄₂ work |

---

## Option 2: WSL2 + tmux (the real thing)

Install Ubuntu from the Microsoft Store, then:

```bash
sudo apt update && sudo apt install -y tmux
```

Mount the project at `/mnt/c/Users/point/projects/RESEARCH_HERMES`.

### Tmux starter script for this project

Save as `~/tmux_aqra.sh` inside WSL:

```bash
#!/bin/bash
SESSION="aqra"
tmux new-session -d -s $SESSION -n main -c /mnt/c/Users/point/projects/RESEARCH_HERMES

tmux split-window -h -t $SESSION:main -c /mnt/c/Users/point/projects/RESEARCH_HERMES/aqra

tmux split-window -v -t $SESSION:main.1 -c /mnt/c/Users/point/projects/RESEARCH_HERMES/docs/superpowers/specs

tmux select-layout -t $SESSION:main main-vertical

tmux attach -t $SESSION
```

Run it: `bash ~/tmux_aqra.sh`

### Essential tmux commands

| Action | Command |
|--------|---------|
| New session | `tmux new -s aqra` |
| Attach | `tmux attach -t aqra` |
| List sessions | `tmux ls` |
| Detach | `Ctrl+b d` |
| New window | `Ctrl+b c` |
| Next window | `Ctrl+b n` |
| Prev window | `Ctrl+b p` |
| Rename window | `Ctrl+b ,` |
| Split vertical | `Ctrl+b %` |
| Split horizontal | `Ctrl+b "` |
| Move pane | `Ctrl+b arrow` |
| Resize pane | `Ctrl+b Ctrl+arrow` or `Ctrl+b :resize-pane -D 5` |
| Zoom pane | `Ctrl+b z` |
| Copy mode | `Ctrl+b [` |
| Paste | `Ctrl+b ]` |
| Kill pane | `Ctrl+b x` |

### Tmux session strategy for RESEARCH_HERMES

| Session | Windows | Use |
|---------|---------|-----|
| `aqra` | `main`, `tests`, `pipeline`, `live` | Code, tests, runs, deploy |
| `paper` | `draft`, `latex`, `review` | Paper writing and review |
| `moonshot` | `attack`, `theory`, `notes` | Honest Agent Protocol experiments + theorem notes |
| `math` | `c42`, `paper` | Prometheus C₄₂ work |

---

## Option 3: MSYS2 with pacman tmux

If you prefer to keep using this exact shell, install MSYS2 from https://www.msys2.org/ and run:

```bash
pacman -S tmux
```

This gives you tmux inside the same MINGW64 environment.

---

## Recommended immediate workflow

For today: use `launch_workspace.cmd` + Windows Terminal shortcuts. It gives you the multi-pane, multi-tab efficiency you want without any installation.

When you want the full tmux experience (detach/reattach, session persistence, copy-mode), set up WSL2 + tmux and use the starter script above.

---

## Productivity tips for this sprint

1. **Keep the `main` pane at project root** for `git status`, `git commit`, and memory edits.
2. **Run long experiments in their own tab or pane** so they don't block your prompt.
3. **Use a dedicated `logs` pane** for `tail -f` or `uv run aqra monitor`.
4. **Before switching tasks**, detach/leave the pane running; come back to it.
5. **For the metered attack experiment**, run it in an isolated pane so the summary is preserved when it finishes.
