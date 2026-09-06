from pathlib import Path

src = Path('.github/workflows/ci.yml').read_text(encoding='utf-8')

replacements = {
    '9207c6011f526bd40abd79649484a1a342585bd4': 'a9031bdc85949321a9707dd59ba44cdcba4a0eb0',
    '5c18e6a2a61680422a59beadfbfdb4e0f2a26a35': '921b038391116fd2f65650b198b504e952067301',
    'if [ "$COUNT" -gt 300 ] || [ "${GITHUB_HEAD_REF:-}" = "sila/sips-pure-identity-20260905" ]; then': 'if [ "$COUNT" -gt 300 ] || [ "${GITHUB_HEAD_REF:-}" = "sila/sips-pure-identity-20260905" ] || [ "${GITHUB_HEAD_REF:-}" = "sila/sips-pure-identity-latest-20260907" ]; then',
    'if [ "$COUNT" -gt 300 ] || [ "${GITHUB_HEAD_REF:-}" = "sila/sips-100pct-completion-20260905" ]; then': 'if [ "$COUNT" -gt 300 ] || [ "${GITHUB_HEAD_REF:-}" = "sila/sips-100pct-completion-20260905" ] || [ "${GITHUB_HEAD_REF:-}" = "sila/sips-pure-identity-latest-20260907" ]; then',
    "re.search(r'(?<![A-Za-z0-9_])(?:EVM|Evm|evm)(?![A-Za-z0-9_])', scrubbed)": "re.search(r'(?i)evm', scrubbed)",
}

for old, new in replacements.items():
    if old not in src:
        raise SystemExit('CI_PATCH_MARKER_MISSING:' + old)
    src = src.replace(old, new)

out = Path('.sila/ci-next.yml')
out.write_text(src, encoding='utf-8')
print('CI_PATCH_PREPARED=PASS')
