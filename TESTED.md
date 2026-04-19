# Test Report

This package was validated structurally in a local container.

## Important compatibility fix

Codex discovers skills from repository `.agents/skills` and user `$HOME/.agents/skills`. The package includes 34 curated repo-scoped skills under `.agents/skills` for direct testing, and the installer copies skills to `$HOME/.agents/skills` for global use.

## Commands run

```bash
python3 -S scripts/validate_codex_package.py
bash scripts/install-codex.sh --dry-run --core --codex-home /tmp/ecc-codex-home --skills-home /tmp/ecc-agent-skills
bash scripts/install-codex.sh --core --no-config --skills-home /tmp/ecc-agent-skills-real
unzip -tq everything-codex-code-v2.zip
```

## Caveat

The local container did not have the `codex` binary installed, so live Codex CLI execution was not claimed. The package was tested for Codex-compatible file layout, TOML parsing, skill metadata validity, install-script behavior, and zip integrity.
