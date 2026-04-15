# Artifact Deck

**Generate reproducible PPTX decks from project notes, status bullets, and screenshots.**

Artifact Deck is a small public OpenClaw skill and local-first Python toolkit for turning
project artifacts into a decision-ready `.pptx`. It builds a clean deck from a JSON manifest,
checks the inputs, renders optional screenshot appendix slides, and prints a rebuild summary
so the same deck can be regenerated without guessing.

Requires Python 3.9+ and `python-pptx`.

## Proof

```md
# Artifact Deck Summary

- Validation: **ok**
- Deck file: **/tmp/artifact-deck-demo/status-review.pptx**
- Slide count: **4**
- Image appendix slides: **1**

## Slides
- Artifact Deck Demo
- What Changed
- Risks And Asks
- Browser Proof
```

## Quick Start

```bash
mkdir -p /tmp/artifact-deck-demo

cat > /tmp/artifact-deck-demo/changes.md <<'EOF'
- CI is green on the release branch.
- ClawHub package was published successfully.
- Public README and release notes were aligned.
EOF

cat > /tmp/artifact-deck-demo/risks.md <<'EOF'
- VirusTotal scan is still pending on one package.
- Need stakeholder approval before promoting the launch post.
EOF

python3 skill/artifact-deck/scripts/init_artifact_deck_manifest.py \
  --title "Artifact Deck Demo" \
  --subtitle "Launch review" \
  --section "What Changed=/tmp/artifact-deck-demo/changes.md" \
  --section "Risks And Asks=/tmp/artifact-deck-demo/risks.md" \
  --out /tmp/artifact-deck-demo/manifest.json

python3 skill/artifact-deck/scripts/check_artifact_deck_inputs.py \
  --manifest /tmp/artifact-deck-demo/manifest.json \
  --out /tmp/artifact-deck-demo/check.json

python3 skill/artifact-deck/scripts/build_artifact_deck.py \
  --manifest /tmp/artifact-deck-demo/manifest.json \
  --deck-out /tmp/artifact-deck-demo/status-review.pptx \
  --out /tmp/artifact-deck-demo/build.json

python3 skill/artifact-deck/scripts/render_artifact_deck_summary.py \
  --manifest /tmp/artifact-deck-demo/manifest.json \
  --check /tmp/artifact-deck-demo/check.json \
  --build /tmp/artifact-deck-demo/build.json \
  --out /tmp/artifact-deck-demo/summary.md
```

## What It Covers

- deterministic `.pptx` generation from a structured manifest
- one default stakeholder deck shape: title, status slides, risks, asks, appendix
- screenshot and diagram appendix slides with captions
- input validation for slide content and image paths before deck generation
- a markdown summary with slide titles and rebuild command

## Included

- `skill/artifact-deck/SKILL.md`
- `skill/artifact-deck/agents/openai.yaml`
- `skill/artifact-deck/scripts/deck_common.py`
- `skill/artifact-deck/scripts/init_artifact_deck_manifest.py`
- `skill/artifact-deck/scripts/check_artifact_deck_inputs.py`
- `skill/artifact-deck/scripts/build_artifact_deck.py`
- `skill/artifact-deck/scripts/render_artifact_deck_summary.py`

## Use Cases

- turn release notes and audit summaries into a stakeholder update deck
- package browser-proof or publish-guard outputs into a client review deck
- convert repo notes and screenshots into a fast executive update
- rebuild a recurring weekly status deck from the same source files

## Limits

- primary output is `.pptx`; PDF export is not built in
- input is curated notes and screenshots, not autonomous research
- one clean default layout, not a template marketplace

## License

MIT
