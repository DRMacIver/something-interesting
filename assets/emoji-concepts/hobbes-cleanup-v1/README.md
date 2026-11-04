# Minimal cleanup attempt

**Approved as emoji bases on 2026-11-04:** `face-cli.png` for 🐯 (U+1F42F)
and `pounce.png` for 🐅 (U+1F405). This approval supersedes the earlier review
status for these two images. Machine-readable selections are recorded in
`approved-bases.json`; production font preparation remains a separate step.

Built-in imagegen was asked to edit each v4 source cutout separately, preserving
the original proportions, expressions and surviving linework. Exact prompts
are saved here. Both inputs were the corresponding white previews in
`../hobbes-source-v4/`.

- `pounce.png`: transparent generated edit. The waist gap is closed, interrupted
  contours repaired and tail tip completed. The tool also smooths the original
  ink noticeably; this is a review candidate, not a pixel-preserving repair.
- Face: no output was produced. The tool returned `moderation_blocked` at the
  output stage with category `other`, request ID
  `5b2ca793-cea9-4a73-8823-912da89626ab`. No specific reason was provided.

Original source cutouts remain unchanged.

## Authorized CLI face edit

After explicit user authorization, the bundled imagegen CLI successfully edited
the face using `gpt-image-2`, high quality, 1024 × 1024, opaque background and
the original white-preview input. The result is `face-cli.png`; the exact
unaugmented prompt is `face-cli-prompt.txt`. The prompt differs from the built-in
attempt only in requesting white background instead of transparency, since the
CLI model does not support transparent output. Broken contours are repaired,
with some additional smoothing of the source ink. The edit took 84 seconds.

The original API output also remains locally at
`output/imagegen/hobbes-face-cleanup-cli-v1.png`. The key was loaded from
`openai.key` via the environment; the key file is excluded by `.gitignore` and
is not included in any prompt, asset or documentation.
