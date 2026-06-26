#!/usr/bin/env python3
"""Delegate a bounded task to one or more external CLI agents.

Universal worker launcher: whichever agent is orchestrating (Claude Code,
Codex, or Antigravity), this runs the OTHERS as bounded sub-workers with safe
defaults, captures only their final message, and (optionally) runs several in
parallel for second-opinion / comparison.

It NEVER enables destructive auto-approval (no codex danger-full-access, no
`--dangerously-skip-permissions`). Two scoped modes exist:
  read-only : analysis / review / planning
              (codex -s read-only ; claude plan ; antigravity --sandbox)
  edit      : bounded code edits
              (codex -s workspace-write ; claude acceptEdits ; antigravity print)

The orchestrator is still responsible for: inspecting `git diff` afterwards,
running verification itself, and never delegating push/deploy/delete.

Worker → binary:  codex→codex · claude→claude · antigravity→agy

Examples
--------
  # Read-only review by Codex
  delegate.py --agent codex --mode read-only --cwd /repo \
      --prompt "Review auth.py for security issues; list by severity."

  # Same prompt to Codex AND Antigravity in parallel, compare locally
  echo "Summarize the architecture in 5 bullets." | \
      delegate.py --agent codex --agent antigravity --cwd /repo

  # Bounded edit by Claude Code
  delegate.py --agent claude --mode edit --cwd /repo --prompt-file task.md
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

AGENTS = ('codex', 'claude', 'antigravity')
BINARIES = {'codex': 'codex', 'claude': 'claude', 'antigravity': 'agy'}


def build_cmd(agent: str, prompt: str, *, mode: str, cwd: str | None,
              model: str | None, add_dirs: list[str], timeout: int,
              out_file: str | None):
    """Return (argv, stdin_data, reads_output_file).

    stdin_data is piped to the process (None → prompt is already on argv).
    reads_output_file → read the final answer from out_file instead of stdout.
    """
    if agent == 'codex':
        sandbox = 'read-only' if mode == 'read-only' else 'workspace-write'
        argv = ['codex', 'exec', '--color', 'never', '--skip-git-repo-check',
                '-s', sandbox]
        if cwd:
            argv += ['-C', cwd]
        if model:
            argv += ['-m', model]
        for d in add_dirs:
            argv += ['--add-dir', d]
        if out_file:
            argv += ['-o', out_file]
        argv.append('-')  # read instructions from stdin
        return argv, prompt, bool(out_file)

    if agent == 'claude':
        perm = 'plan' if mode == 'read-only' else 'acceptEdits'
        argv = ['claude', '--print', '--permission-mode', perm]
        if model:
            argv += ['--model', model]
        if cwd:
            argv += ['--add-dir', cwd]
        for d in add_dirs:
            argv += ['--add-dir', d]
        return argv, prompt, False  # prompt via stdin, answer on stdout

    if agent == 'antigravity':
        # agy -p runs a single prompt non-interactively. --sandbox restricts the
        # terminal for read-only work. We never pass --dangerously-skip-permissions.
        argv = ['agy', '-p', prompt, '--print-timeout', f'{timeout}s']
        if mode == 'read-only':
            argv.append('--sandbox')
        if model:
            argv += ['--model', model]
        for d in add_dirs:
            argv += ['--add-dir', d]
        return argv, None, False  # prompt on argv, answer on stdout

    raise ValueError(f'unknown agent {agent!r}')


def run_agent(agent: str, prompt: str, args) -> dict:
    rec: dict = {'agent': agent}
    binary = BINARIES[agent]
    if shutil.which(binary) is None:
        rec.update(ok=False, error=f'{binary} binary not found on PATH', skipped=True)
        return rec

    out_file = None
    if agent == 'codex':
        out_file = tempfile.NamedTemporaryFile(
            prefix=f'delegate-{agent}-', suffix='.txt', delete=False).name

    argv, stdin_data, reads_file = build_cmd(
        agent, prompt, mode=args.mode, cwd=args.cwd, model=args.model,
        add_dirs=args.add_dir or [], timeout=args.timeout, out_file=out_file)

    rec['cmd'] = ' '.join(a if a != prompt else '<prompt>' for a in argv)
    started = time.time()
    try:
        proc = subprocess.run(
            argv, input=stdin_data, capture_output=True, text=True,
            cwd=args.cwd or None, timeout=args.timeout + 30)
    except subprocess.TimeoutExpired:
        rec.update(ok=False, error=f'timed out after {args.timeout + 30}s')
        return rec
    except Exception as e:  # noqa: BLE001
        rec.update(ok=False, error=repr(e))
        return rec
    rec['elapsed_s'] = round(time.time() - started, 1)
    rec['returncode'] = proc.returncode

    output = proc.stdout
    if reads_file and out_file:
        try:
            with open(out_file, encoding='utf-8') as fh:
                file_out = fh.read().strip()
            if file_out:
                output = file_out
        except OSError:
            pass

    rec['output'] = (output or '').strip()
    if proc.returncode != 0:
        rec['ok'] = False
        rec['stderr'] = (proc.stderr or '').strip()[-2000:]
    else:
        rec['ok'] = True
    return rec


def read_prompt(args) -> str:
    if args.prompt:
        return args.prompt
    if args.prompt_file:
        with open(args.prompt_file, encoding='utf-8') as fh:
            return fh.read()
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data.strip():
            return data
    sys.exit('No prompt: use --prompt, --prompt-file, or pipe via stdin.')


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--agent', action='append', choices=AGENTS,
                    help='Target agent (repeatable). Omit with --all.')
    ap.add_argument('--all', action='store_true',
                    help='Delegate to every available agent (codex, claude, antigravity)')
    ap.add_argument('--mode', choices=('read-only', 'edit'), default='read-only',
                    help='read-only (default) = analysis/review; edit = bounded code edits')
    ap.add_argument('--prompt', help='Prompt text')
    ap.add_argument('--prompt-file', help='Read prompt from this file')
    ap.add_argument('--cwd', help='Working root / context dir for the worker')
    ap.add_argument('--model', help='Override the worker model (agent-specific alias)')
    ap.add_argument('--add-dir', action='append',
                    help='Extra readable/writable dir (repeatable)')
    ap.add_argument('--timeout', type=int, default=600,
                    help='Per-agent timeout in seconds (default 600)')
    ap.add_argument('--json', action='store_true',
                    help='Emit machine-readable JSON instead of labeled text')
    args = ap.parse_args()

    targets = list(dict.fromkeys(args.agent or []))
    if args.all:
        targets = list(AGENTS)
    if not targets:
        ap.error('Pick at least one --agent, or pass --all')

    prompt = read_prompt(args)

    if len(targets) == 1:
        results = [run_agent(targets[0], prompt, args)]
    else:
        with ThreadPoolExecutor(max_workers=len(targets)) as ex:
            results = list(ex.map(lambda a: run_agent(a, prompt, args), targets))

    if args.json:
        print(json.dumps({'mode': args.mode, 'results': results},
                         indent=2, ensure_ascii=False))
    else:
        for r in results:
            head = f"===== {r['agent']} ({'ok' if r.get('ok') else 'FAILED'}"
            if 'elapsed_s' in r:
                head += f", {r['elapsed_s']}s"
            head += ') ====='
            print(head)
            if r.get('skipped') or not r.get('ok'):
                print(r.get('error') or r.get('stderr') or '(no error detail)')
            if r.get('output'):
                print(r['output'])
            print()

    # Exit non-zero only if every target failed
    sys.exit(0 if any(r.get('ok') for r in results) else 1)


if __name__ == '__main__':
    main()
