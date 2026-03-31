# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-03-31

### Documentation

- Add mkdocs-shadcn documentation site (#3)
- Trigger docs deployment on version tag push instead of main push
- Merge docs deployment into publish workflow
- Merge docs-build and docs-deploy into single docs job
- Remove Next Steps section from main page

### Features

- Add optional description field to rules (#4)
## [0.2.0] - 2026-03-31

### Bug Fixes

- Add gitmoji prefix to publish workflow commit message

### Documentation

- Add inline ignore comment section to README

### Features

- Add rule name validation (#1)
- ignore) (#2)

### Testing

- Add decorator filter tests for function and class checkers
## [0.1.0] - 2026-03-30

### Documentation

- Write comprehensive README with examples and configuration guide

### Features

- Add config parsing for rules and apply sections
- Add module pattern matcher with wildcard and capture support
- Add Violation dataclass for checker results
- Add variable name checker with source/transform and case support
- Add function/method name checker with filter and prefix support
- Add class name checker with base_class filter and regex support
- Add module name checker with class_name derivation and regex
- Add package name checker with case and regex support
- line output format
- Add CLI with pnl check command and end-to-end integration

### Miscellaneous

- Set up project scaffolding and tooling
- Add runtime dependencies and CLI entry point
- Fix ruff lint and format issues
