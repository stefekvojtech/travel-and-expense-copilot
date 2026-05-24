"""Deploy the committed repository snapshot to the Hugging Face Space.

This script does not read `.env` and does not store Hugging Face credentials in
the repo. It uses an existing Hugging Face login token or the Git credential
stored for `https://huggingface.co`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

from huggingface_hub import HfApi, get_token


DEFAULT_REPO_ID = "stefekvojtech/travel-and-expense-copilot"
TERMINAL_FAILURE_STAGES = {"BUILD_ERROR", "RUNTIME_ERROR"}
SUCCESS_STAGE = "RUNNING"


def main() -> int:
    configure_output()

    parser = argparse.ArgumentParser(
        description="Upload HEAD to the Hugging Face Space and wait for the build."
    )
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID)
    parser.add_argument(
        "--commit-message",
        default="Deploy current main to Hugging Face Space",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=900,
        help="Maximum time to wait for the Space to report RUNNING.",
    )
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=15,
        help="Seconds between Space status checks.",
    )
    args = parser.parse_args()

    token = resolve_hf_token()
    api = HfApi(token=token)

    repo_root = get_repo_root()
    ensure_clean_head(repo_root)

    with tempfile.TemporaryDirectory(prefix="hf-space-deploy-") as temp_dir:
        temp_path = Path(temp_dir)
        archive_path = temp_path / "repo.tar"
        export_path = temp_path / "export"
        export_path.mkdir()

        print("Exporting committed HEAD...")
        run(["git", "archive", "HEAD", "-o", str(archive_path)], cwd=repo_root)

        print("Preparing clean upload folder...")
        with tarfile.open(archive_path) as archive:
            archive.extractall(export_path, filter="data")

        print(f"Uploading to Hugging Face Space: {args.repo_id}")
        commit_info = api.upload_folder(
            repo_id=args.repo_id,
            repo_type="space",
            folder_path=export_path,
            commit_message=args.commit_message,
            delete_patterns="*",
            token=token,
        )
        print(f"Uploaded Space commit: {commit_info.commit_url}")

    print("Temporary deployment files cleaned up.")
    return wait_for_space(api, token, args.repo_id, args.timeout_seconds, args.poll_seconds)


def resolve_hf_token() -> str:
    cached_token = get_token()
    if cached_token:
        return cached_token

    credential_token = get_git_credential_token()
    if credential_token:
        return credential_token

    raise SystemExit(
        "No Hugging Face token found. Run `hf auth login` or store a Git "
        "credential for https://huggingface.co."
    )


def get_git_credential_token() -> str | None:
    credential_input = "protocol=https\nhost=huggingface.co\n\n"
    result = subprocess.run(
        ["git", "credential", "fill"],
        input=credential_input,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():
        if line.startswith("password="):
            return line.removeprefix("password=")
    return None


def get_repo_root() -> Path:
    result = run(["git", "rev-parse", "--show-toplevel"], capture_output=True)
    return Path(result.stdout.strip())


def ensure_clean_head(repo_root: Path) -> None:
    result = run(["git", "status", "--short"], cwd=repo_root, capture_output=True)
    if result.stdout.strip():
        raise SystemExit(
            "Working tree has uncommitted changes. Commit or stash them before deployment."
        )


def wait_for_space(
    api: HfApi,
    token: str,
    repo_id: str,
    timeout_seconds: int,
    poll_seconds: int,
) -> int:
    print("Waiting for Hugging Face build/runtime status...")
    deadline = time.monotonic() + timeout_seconds
    printed_log_chars = 0
    last_stage = ""

    while time.monotonic() < deadline:
        runtime = api.get_space_runtime(repo_id, token=token)
        stage = normalize_stage(runtime.stage)
        if stage != last_stage:
            print(f"Space status: {stage}")
            last_stage = stage

        printed_log_chars = print_new_build_logs(api, token, repo_id, printed_log_chars)

        if stage == SUCCESS_STAGE:
            print("Deployment successful: Space is RUNNING.")
            return 0
        if stage in TERMINAL_FAILURE_STAGES:
            print_new_build_logs(api, token, repo_id, printed_log_chars)
            print(f"Deployment failed: Space reported {stage}.")
            return 1

        time.sleep(max(1, poll_seconds))

    print_new_build_logs(api, token, repo_id, printed_log_chars)
    print(f"Deployment timed out after {timeout_seconds} seconds.")
    return 1


def print_new_build_logs(api: HfApi, token: str, repo_id: str, printed_chars: int) -> int:
    try:
        log_text = "".join(api.fetch_space_logs(repo_id, build=True, token=token))
    except Exception as exc:  # pragma: no cover - network/API behavior
        print(f"Could not fetch build logs yet: {exc}")
        return printed_chars

    if len(log_text) <= printed_chars:
        return printed_chars

    new_text = log_text[printed_chars:]
    print(new_text, end="" if new_text.endswith("\n") else "\n")
    return len(log_text)


def normalize_stage(stage: object) -> str:
    value = getattr(stage, "value", stage)
    return str(value).upper()


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=capture_output,
        check=True,
    )


def configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    sys.exit(main())
