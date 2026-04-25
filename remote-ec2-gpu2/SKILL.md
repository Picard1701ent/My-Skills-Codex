---
name: remote-ec2-gpu2
description: Use when the user wants Codex on this machine to connect to, inspect, or operate the peer EC2 server over SSH. Covers connectivity checks, remote command execution, tmux-based long runs, log inspection, and file transfer conventions for the remote host aliased as gpu2.
---

# Remote EC2 gpu2

## Overview

This machine is the control node. The peer EC2 server should be accessed through the local SSH alias `gpu2`, not by retyping raw connection details unless debugging the SSH config itself.

Current remote target:
- SSH alias: `gpu2`
- Remote host: `172.31.33.255`
- Remote user: `ubuntu`
- SSH key on this machine: `~/.ssh/XudongChen.pem`
- SSH config file: `~/.ssh/config`

## When To Use

Use this skill when the user asks to:
- connect to the peer EC2 server
- run code, training, evaluation, or shell commands on the peer EC2 server
- verify whether the peer EC2 server is reachable after reboot
- inspect logs, processes, GPUs, or tmux sessions on the peer EC2 server
- copy files between this machine and the peer EC2 server

## Standard Workflow

1. Confirm the SSH alias exists before assuming connectivity:

```bash
ssh -G gpu2 | sed -n '1,40p'
```

2. For a quick connectivity check, prefer a short non-interactive command:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 gpu2 'hostname && whoami && pwd'
```

3. For one-off remote execution, run through the alias:

```bash
ssh gpu2 'cd ~/repo && python your_script.py'
```

4. For long-running jobs, use `tmux` on the remote host:

```bash
ssh gpu2 'tmux new -d -s job "cd ~/repo && python train.py > train.log 2>&1"'
ssh gpu2 'tmux ls'
ssh gpu2 'tail -n 100 ~/repo/train.log'
```

5. For interactive work, open a shell session:

```bash
ssh gpu2
```

## File Transfer

Copy from this machine to the remote host:

```bash
scp /path/to/local.file gpu2:/path/to/remote.file
```

Copy from the remote host to this machine:

```bash
scp gpu2:/path/to/remote.file /path/to/local.file
```

For directories:

```bash
scp -r /path/to/local_dir gpu2:/path/to/remote_dir
scp -r gpu2:/path/to/remote_dir /path/to/local_dir
```

## Safety And Operating Rules

- Prefer the alias `gpu2` over raw IPs so future host changes stay localized to `~/.ssh/config`.
- Do not overwrite or move `~/.ssh/XudongChen.pem` unless the user explicitly asks.
- Treat remote commands as high-impact. Avoid destructive operations unless the user explicitly requested them.
- Before launching expensive jobs, verify the target path, environment, and available GPU or disk state on the remote host.
- When checking connectivity from Codex, real SSH probes may require escalated execution because the local sandbox can block outbound sockets.

## Useful Remote Checks

```bash
ssh gpu2 'hostname -I'
ssh gpu2 'nvidia-smi'
ssh gpu2 'df -h'
ssh gpu2 'free -h'
ssh gpu2 'ps -ef | grep python'
ssh gpu2 'tmux ls'
```

## Notes

- The peer EC2 server has already been verified as reachable from this machine over private IP.
- After a normal reboot, the peer server remained reachable at `172.31.33.255` during prior testing.
