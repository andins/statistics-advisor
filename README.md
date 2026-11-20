# Statistics Advisor skill

An [Agent Skills](https://agentskills.io) folder (`SKILL.md`, references, helper scripts) that makes an AI agent answer statistics questions the same way every time: triage first, assumptions checked, estimates with intervals, sources cited.

| Folder | What it is |
|---|---|
| [`statistics-advisor/`](./statistics-advisor) | The skill itself: `SKILL.md`, `references/` (triage logic, citation list, test-vs-regression equivalents) and `scripts/` (runnable reference templates for EDA, power analysis, regression/GLM modeling, assumption checks, causal DAGs, clustered/time-series data, meta-analysis, and a worked t-test-vs-regression example). |
| [`tools/`](./tools) | Scripts to install the skill into an agent tool, to package it for web chats, and to test both of the above. |

This skill is self-contained: nothing under `statistics-advisor/` links to or depends on anything outside this repository.

## License

[MIT](./LICENSE).

## Quick start

```
python3 tools/install_skill.py --tool claude              # for Claude Code, all your projects
python3 tools/install_skill.py --tool copilot             # for VS Code chat (GitHub Copilot)
python3 tools/install_skill.py --tool agents              # for Codex (and other tools reading ~/.agents)
python3 tools/install_skill.py --tool claude --project ~/projects/my-first-analysis
python3 tools/install_skill.py --tool gemini --dry-run    # show what would happen
```

To update: `git pull`, then run the same command again; the old copy is replaced.

The installer and packager need only the Python standard library. Run from anywhere; the skill is found relative to `tools/`, so it does not matter what the repository folder is called (for example after downloading a ZIP).

## For maintainers

Everything below runs from this folder. Testing the reference templates (`test_skill_templates.py`) needs the scientific Python stack — install it with `uv sync` (see `pyproject.toml`); that test skips itself when the stack is missing.

| Task | Command |
|---|---|
| Test the skill packaging, installer, and reference templates | `cd tools && python3 -m unittest test_skill_package test_install_skill test_skill_templates` |
| Build the Claude web-app zip and the single-file version for other chats | `python3 tools/package_skill.py` (writes `dist/`) |
