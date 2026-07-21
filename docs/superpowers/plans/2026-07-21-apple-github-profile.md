# Apple GitHub Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild `LiangLiang723/LiangLiang723` as an Apple-inspired GitHub profile with automatic light/dark theme switching, repository-local visual assets, reliable generated statistics, and reduced-motion-friendly presentation.

**Architecture:** `README.md` owns structure and theme selection through `<picture>` elements. `.github/scripts/generate_apple_assets.py` deterministically generates all local light/dark SVG cards under `assets/apple/`; `.github/scripts/validate_profile.py` validates XML, links, theme pairs, forbidden external dependencies, and workflow configuration. `.github/workflows/profile.yml` generates only `github` and `github_dark` summary-card themes plus both contribution-snake variants.

**Tech Stack:** Markdown, HTML `<picture>`, SVG/XML, Python 3 standard library, YAML, GitHub Actions.

## Global Constraints

- Use the approved Apple compact layout: hero, profile, technical capabilities, four projects, development data, contribution trail, current focus, and footer.
- Automatically switch every custom visual and statistics card using `prefers-color-scheme`.
- Store every custom visual in the repository; do not use `img.shields.io`, online banner generators, or `github-readme-stats.vercel.app`.
- Use system fonts, restrained materials, large spacing, soft shadows, and Apple system blue.
- Do not use looping glow, flashing, moving backgrounds, or large continuous animation.
- Every SVG must contain `<title>`, `<desc>`, `width="1200"`, a matching `viewBox`, and reduced-motion handling.
- Every `<picture>` must provide a light default fallback.
- Keep the four featured projects independently clickable.
- Preserve light and dark contribution-snake variants from the repository `output` branch.

---

## Task 1: Deterministic validation

**Files:** Create `.github/scripts/validate_profile.py`.

- [ ] Define the exact 18 expected `assets/apple/*.svg` files.
- [ ] Parse all generated SVG files with `xml.etree.ElementTree`.
- [ ] Validate accessibility metadata, dimensions, theme pairs, local references, section count, featured project URLs, statistics themes, workflow wiring, and absence of obsolete assets.
- [ ] Run a deliberate broken-theme-pair fixture and verify the script exits non-zero.
- [ ] Restore the valid README and verify `Profile validation passed.`.

## Task 2: Apple visual asset generator

**Files:** Create `.github/scripts/generate_apple_assets.py` and 18 files under `assets/apple/`.

- [ ] Define immutable light and dark theme tokens.
- [ ] Implement reusable SVG document, material-card, text, pill, and divider helpers.
- [ ] Implement renderers for hero, profile, technical capabilities, project cards, focus cards, and footer.
- [ ] Generate nine light/dark pairs: hero, profile, technical capabilities, four projects, focus, and footer.
- [ ] Run the generator twice and verify identical SHA-256 hashes.
- [ ] Parse all 18 outputs as XML.

## Task 3: Apple compact README

**Files:** Replace `README.md`.

- [ ] Use the confirmed section order: hero, about, technical capabilities, featured projects, development data, contribution trail, current focus, footer.
- [ ] Use `<picture>` with dark source, light source, and light `<img>` fallback for every local asset and statistics card.
- [ ] Put the four project cards in a two-column layout while retaining independent repository links.
- [ ] Reference only `github` and `github_dark` generated statistics.
- [ ] Keep the existing light/dark contribution snake.

## Task 4: Workflow update

**Files:** Replace `.github/workflows/profile.yml`.

- [ ] Add validation for pushes and pull requests affecting profile files.
- [ ] Generate `github` and `github_dark` summary-card themes in separate action steps with `AUTO_PUSH: false`.
- [ ] Validate before committing generated statistics.
- [ ] Commit only changed summary-card directories.
- [ ] Continue generating light/dark contribution-snake assets on the `output` branch.

## Task 5: Cleanup and verification

**Files:** Delete `assets/header.svg`, `assets/profile-badges.svg`, `assets/tech-stack.svg`, and `assets/footer-line.svg`.

- [ ] Run the generator, validator, Python bytecode compilation, XML parsing, YAML parsing, forbidden-reference scan, and deterministic-output comparison.
- [ ] Render representative light and dark SVG files and visually inspect layout, contrast, typography, and clipping.
- [ ] Verify the remote branch contains all expected files and no old visual references.
- [ ] Merge the reviewed branch into `main` using squash merge.
