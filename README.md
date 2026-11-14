# SVG Sheriff

**A local-first quality gate for SVG accessibility, animation and unsafe markup.**

SVG Sheriff scans SVG files locally, with no uploads and no runtime dependencies. It flags missing accessible names, responsive sizing risks, motion that needs a reduced-motion strategy, and unsafe active content.

## Install

```bash
python -m pip install .
```
Requires Python 3.10+.

## Usage

```bash
svg-sheriff assets/*.svg
svg-sheriff --strict --format json logo.svg
```

Exit status is 1 when an error is found; `--strict` also fails on warnings. JSON output is suitable for CI integration.

## Checks

| Rule | Severity | Meaning |
|---|---|---|
| A11Y001 | warning | No accessible title or name |
| SVG003 | warning | Missing responsive viewBox |
| MOTION001 | warning | Animation needs reduced-motion review |
| SEC001 / SEC002 | error | Active content or inline event handler |
| SEC003 | error | Disallowed URL scheme |
| SEC004 | warning | External resource reference |

This is a static heuristic scanner, not a substitute for browser testing or a full accessibility audit. It flags motion for human review; it does not claim to prove that a static fallback exists.

## Development

```bash
python -m unittest discover -s tests -v
```

## License

MIT.
