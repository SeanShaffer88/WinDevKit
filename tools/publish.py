#!/usr/bin/env python3
"""WinDevKit publisher — publish local files to a GitHub repo via the
GitHub connector's Contents API (create_or_update_file), safely.

Hard-won rules baked in (each cost a real incident):
  * create_or_update_file takes PLAIN file content. Never pre-base64-encode
    (ModernFlyouts PR #1 landed 12 files as base64 blobs; repaired in PR #2).
  * One file per call: push_files (Git Trees) 403s on this GitHub App.
  * Keep a file's JSON-encoded form under ~105 KB — the publish path passes
    content as one argv string and the OS caps it at 131,072 bytes
    (InstallScope's 132 KB cli.rs had to be split into modules).
  * .github/workflows/* cannot be written by the App (no Workflows
    permission) — those files go through the browser UI. This tool refuses
    them with that explanation instead of failing mysteriously.
  * Always read back and compare SHA-256 after publishing (--verify,
    on by default): "the call succeeded" is not "the file is correct".

Usage:
  publish.py --owner SeanShaffer88 --repo WinRecovery --branch main \\
             --root ~/workspace/winrecovery \\
             --message "Commit message" \\
             path/in/repo=local/file [more pairs...]
  publish.py ... --files-from git   # every file in the latest local commit
  publish.py ... --dry-run           # validate + report, publish nothing

Requires the Muse GitHub connector CLI at /opt/hatch/bin/github.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request

GH = "/opt/hatch/bin/github"
SIZE_LIMIT = 105_000  # bytes, JSON-encoded form, with margin


def gh_call(tool, args, read=False):
    cmd = [GH, "call-read-tool" if read else "call-tool",
           "--name", tool, "--arguments-json", json.dumps(args)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    try:
        response = json.loads(r.stdout)
    except (ValueError, TypeError):
        response = None
    if tool == "get_file_contents" and isinstance(response, dict) and (
        response.get("status") == 404 or response.get("status_code") == 404
    ):
        raise FileNotFoundError("remote file does not exist")
    if r.returncode:
        raise RuntimeError(f"connector command failed (exit {r.returncode}): {r.stderr[-300:]}")
    if isinstance(response, dict) and (
        response.get("isError") is True or response.get("success") is False
        or response.get("status") == "ERROR" or response.get("error")
    ):
        raise RuntimeError("connector reported an error response")
    return r.stdout or "", r.stderr or ""


def current_sha(owner, repo, path, branch):
    try:
        out, _ = gh_call("get_file_contents",
                         {"owner": owner, "repo": repo, "path": path, "ref": branch},
                         read=True)
    except FileNotFoundError:
        return None
    # The connector reports: successfully downloaded text file (SHA: abc123…)
    m = re.search(r"SHA:\s*([0-9a-f]{40})", out)
    if not m:
        try:
            value = json.loads(out)
        except ValueError:
            value = {}
        sha = value.get("sha") if isinstance(value, dict) else None
        if isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha):
            return sha
        raise RuntimeError("unrecognized remote file response; refusing to assume the file is absent")
    return m.group(1)


def raw_bytes(owner, repo, path, branch):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--branch", default="main")
    ap.add_argument("--root", required=True, help="local directory files are read from")
    ap.add_argument("--message", required=True)
    ap.add_argument("--files-from", choices=["git", "git-tree"],
                    help="'git': files changed in the latest commit; "
                         "'git-tree': every tracked file at HEAD (initial publish)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("pairs", nargs="*", help="repo_path=local_path (local defaults to repo_path)")
    a = ap.parse_args()

    import os
    pairs = []
    if a.files_from == "git":
        # --root matters: without it diff-tree prints nothing for a root commit.
        r = subprocess.run(["git", "-C", a.root, "diff-tree", "--root",
                            "--no-commit-id", "--name-only", "-r", "HEAD"],
                           capture_output=True, text=True, check=True)
        for line in r.stdout.splitlines():
            if line.strip():
                pairs.append((line.strip(), line.strip()))
    if a.files_from == "git-tree":
        r = subprocess.run(["git", "-C", a.root, "ls-tree", "-r", "--name-only", "HEAD"],
                           capture_output=True, text=True, check=True)
        for line in r.stdout.splitlines():
            if line.strip():
                pairs.append((line.strip(), line.strip()))
    for p in a.pairs:
        if "=" in p:
            repo_path, local = p.split("=", 1)
        else:
            repo_path = local = p
        pairs.append((repo_path, local))
    if not pairs:
        sys.exit("nothing to publish")

    failures = 0
    for repo_path, local in pairs:
        if repo_path.startswith(".github/workflows/"):
            print(f"REFUSED {repo_path}: the GitHub App cannot write workflow "
                  "files; add this one through the browser UI.")
            failures += 1
            continue
        local_path = os.path.join(a.root, local)
        try:
            with open(local_path, "rb") as fh:
                data = fh.read()
        except OSError as e:
            print(f"MISSING {local_path}: {e}")
            failures += 1
            continue
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError:
            print(f"REFUSED {repo_path}: not UTF-8 text; this publisher is for "
                  "text files (binary publishing needs the snapshot route).")
            failures += 1
            continue
        encoded = len(json.dumps(content))
        if encoded > SIZE_LIMIT:
            print(f"TOO BIG {repo_path}: JSON form is {encoded} bytes "
                  f"(limit ~{SIZE_LIMIT}); split the file into modules first.")
            failures += 1
            continue
        if a.dry_run:
            print(f"DRY-RUN ok {repo_path} ({len(data)} bytes, sha256 "
                  f"{hashlib.sha256(data).hexdigest()[:12]}…)")
            continue
        args = {"owner": a.owner, "repo": a.repo, "branch": a.branch,
                "path": repo_path, "message": a.message, "content": content}
        try:
            sha = current_sha(a.owner, a.repo, repo_path, a.branch)
            if sha:
                args["sha"] = sha
            out, err = gh_call("create_or_update_file", args)
            if re.search(r"(?im)^\s*(error|failed|failure)\b", out + "\n" + err):
                raise RuntimeError((out + err)[-200:])
        except (OSError, RuntimeError, subprocess.SubprocessError) as e:
            print(f"FAILED {repo_path}: {e}")
            failures += 1
            continue
        print(f"published {repo_path}")
        if not a.no_verify:
            try:
                remote = raw_bytes(a.owner, a.repo, repo_path, a.branch)
                if hashlib.sha256(remote).digest() == hashlib.sha256(data).digest():
                    print(f"  verified sha256 match")
                else:
                    print(f"  VERIFY MISMATCH {repo_path} — remote differs from local!")
                    failures += 1
            except Exception as e:  # raw CDN can lag a few seconds
                print(f"  VERIFY FAILED {repo_path}: {e}; success is unconfirmed")
                failures += 1
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
