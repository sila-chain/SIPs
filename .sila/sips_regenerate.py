from __future__ import annotations

from pathlib import Path
import os
import re
import shutil
import sys

if len(sys.argv) != 3:
    raise SystemExit('USAGE: sips_regenerate.py <upstream-worktree> <output-dir>')

SRC = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()

if not SRC.is_dir():
    raise SystemExit(f'UPSTREAM_SOURCE_MISSING:{SRC}')

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

PROTECTED_CONTENT_PATTERNS = [
    r'(?:(?:https?://)?github\.com/ethereum/go-ethereum(?:[^\s\)\]\}\>\"\']*)?)',
    r'(?:(?:https?://)?github\.com/ethereum/eth2\.0-specs(?:[^\s\)\]\}\>\"\']*)?)',
    r'(?:(?:https?://)?github\.com/ethereum/eth2spec(?:[^\s\)\]\}\>\"\']*)?)',
    r'(?<![A-Za-z0-9_])ethereum/go-ethereum(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])ethereum/eth2\.0-specs(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])ethereum/eth2spec(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])go-ethereum(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])GETH_NAME(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])(?:geth|Geth|GETH)(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])eth_[A-Za-z0-9_]+(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])eth2spec(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])eth2\.0-specs(?![A-Za-z0-9_])',
]

PROTECTED_PATH_PATTERNS = [
    r'(?<![A-Za-z0-9_])go-ethereum(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])(?:geth|Geth|GETH)(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])eth2spec(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])eth2\.0-specs(?![A-Za-z0-9_])',
]

PROTECTED_CONTENT = [re.compile(p) for p in PROTECTED_CONTENT_PATTERNS]
PROTECTED_PATH = [re.compile(p) for p in PROTECTED_PATH_PATTERNS]

URL_RE = re.compile(r'https?://[^\s\)\]\}\>\"\']+')
ETH_RESEARCH_MD_RE = re.compile(
    r'\[([^\]]+)\]\(https?://ethresear\.ch/[^\)]+\)'
)


def mask_matches(text: str, patterns: list[re.Pattern[str]], prefix: str):
    saved: list[str] = []

    def repl(m: re.Match[str]) -> str:
        token = f'__{prefix}_{len(saved):06d}__'
        saved.append(m.group(0))
        return token

    for pat in patterns:
        text = pat.sub(repl, text)
    return text, saved


def restore_matches(text: str, saved: list[str], prefix: str) -> str:
    for i, value in enumerate(saved):
        text = text.replace(f'__{prefix}_{i:06d}__', value)
    return text


def case_token(token: str, upper: str, title: str, lower: str) -> str:
    if token.isupper():
        return upper
    if token[:1].isupper():
        return title
    return lower


def dense_identity(text: str) -> str:
    def eip_repl(m: re.Match[str]) -> str:
        return case_token(m.group(0), 'SIP', 'Sip', 'sip')

    def erc_repl(m: re.Match[str]) -> str:
        return case_token(m.group(0), 'SRC', 'Src', 'src')

    def eth_dense_repl(m: re.Match[str]) -> str:
        return case_token(m.group(0), 'SIL', 'Sil', 'sil')

    def evm_dense_repl(m: re.Match[str]) -> str:
        return case_token(m.group(0), 'SVM', 'Svm', 'svm')

    text = re.sub(
        r'(?<![A-Za-z0-9])(?:EIP|Eip|eip)(?=[A-Za-z0-9_.-])',
        eip_repl,
        text,
    )
    text = re.sub(
        r'(?<![A-Za-z0-9])(?:ERC|Erc|erc)(?=[A-Za-z0-9_.-])',
        erc_repl,
        text,
    )
    text = re.sub(
        r'(?<![A-Za-z0-9])(?:ETH|Eth|eth)(?=[0-9_-])',
        eth_dense_repl,
        text,
    )
    text = re.sub(
        r'(?<![A-Za-z0-9])(?:ETH|Eth|eth)(?=falcon)',
        eth_dense_repl,
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'(?<![A-Za-z0-9])(?:EVM|Evm|evm)(?=[A-Za-z0-9_.-])',
        evm_dense_repl,
        text,
    )
    text = text.replace('gasEVM', 'gasSVM').replace('gasevm', 'gassvm')
    return text


def transform_official_url(url: str) -> str | None:
    lower = url.lower()

    if 'ethresear.ch/' in lower:
        return None

    official = (
        'github.com/ethereum/' in lower
        or 'raw.githubusercontent.com/ethereum/' in lower
        or 'ethereum.org' in lower
        or 'ethereum-magicians.org' in lower
        or 'ethereum.stackexchange.com' in lower
        or 'eips.ethereum.org' in lower
    )

    if not official:
        return url

    if re.search(
        r'github\.com/ethereum/(?:go-ethereum|eth2\.0-specs|eth2spec)(?:/|$)',
        url,
    ):
        return url

    url = re.sub(r'github\.com/ethereum/', 'github.com/sila-chain/', url)
    url = re.sub(
        r'raw\.githubusercontent\.com/ethereum/',
        'raw.githubusercontent.com/sila-chain/',
        url,
    )
    url = url.replace('eips.ethereum.org', 'sips.sila.org')
    url = url.replace('ethereum-magicians.org', 'sila-magicians.org')
    url = url.replace('ethereum.stackexchange.com', 'sila.stackexchange.com')
    url = url.replace('notes.ethereum.org', 'notes.sila.org')
    url = url.replace('blog.ethereum.org', 'blog.sila.org')
    url = url.replace('ethereum.org', 'sila.org')
    return dense_identity(url)


def transform_text(text: str) -> str:
    text = ETH_RESEARCH_MD_RE.sub(
        lambda m: f'{m.group(1)} in Sila Research',
        text,
    )

    text, protected = mask_matches(
        text,
        PROTECTED_CONTENT,
        'SILA_CONTENT_PROTECTED',
    )

    third_party_urls: list[str] = []

    def url_repl(m: re.Match[str]) -> str:
        original = m.group(0)
        transformed = transform_official_url(original)
        if transformed is None:
            return 'Sila Research'
        if transformed != original:
            return transformed
        token = f'__SILA_THIRD_URL_{len(third_party_urls):06d}__'
        third_party_urls.append(original)
        return token

    text = URL_RE.sub(url_repl, text)

    exact = [
        ('eip-review-bot', 'sip-review-bot'),
        ('EIP-Review-Bot', 'SIP-Review-Bot'),
        ('eipw-action', 'sipw-action'),
        ('EIPW', 'SIPW'),
        ('eipw', 'sipw'),
        ('IWETH', 'IWSIL'),
        ('WETH', 'WSIL'),
        ('IERC', 'ISRC'),
        ('AERC', 'ASRC'),
        ('IEIP', 'ISIP'),
        ('Ethereum Foundation', 'Sila Foundation'),
        ('ethereum Foundation', 'Sila Foundation'),
        ('Ethereum Magicians', 'Sila Magicians'),
        ('Ethereum Stack Exchange', 'Sila Stack Exchange'),
        ('Ethereum Research', 'Sila Research'),
        ('Etherscan', 'SilaScan'),
        ('etherscan', 'silascan'),
        ('ethereumjs', 'silajs'),
        ('EthereumJS', 'SilaJS'),
        ('@ethereumjs', '@silajs'),
        ('/eth2/', '/sila/'),
        ('/eth/', '/sila/'),
    ]

    for a, b in exact:
        text = text.replace(a, b)

    text = re.sub(r'(?<![A-Za-z0-9_.-])ethereum/', 'sila-chain/', text)
    text = dense_identity(text)

    word_rules = [
        ('ERCS', 'SRCS'), ('ERCs', 'SRCs'), ('ercs', 'srcs'),
        ('ERC', 'SRC'), ('erc', 'src'),
        ('EIPS', 'SIPS'), ('EIPs', 'SIPs'), ('eips', 'sips'),
        ('EIP', 'SIP'), ('eip', 'sip'),
        ('ETHEREUM', 'SILA'), ('Ethereum', 'Sila'), ('ethereum', 'sila'),
        ('Ether', 'Sila'), ('ether', 'sila'),
        ('ETH', 'SIL'), ('Eth', 'Sil'), ('eth', 'sil'),
        ('EVM', 'SVM'), ('Evm', 'Svm'), ('evm', 'svm'),
        ('Mainnet', 'SilaMainnet'), ('MAINNET', 'SILA_MAINNET'), ('mainnet', 'sila-mainnet'),
        ('Sepolia', 'SilaSepolia'), ('Holesky', 'SilaHolesky'),
        ('Deneb', 'SilaDeneb'), ('Fulu', 'SilaFulu'), ('PeerDAS', 'SilaPeerDAS'),
        ('Cancun', 'SilaCancun'), ('Shanghai', 'SilaShanghai'),
        ('Prague', 'SilaPrague'), ('Osaka', 'SilaOsaka'),
        ('Paris', 'SilaParis'), ('Amsterdam', 'SilaAmsterdam'),
        ('Kovan', 'SilaKovan'),
    ]

    for a, b in word_rules:
        text = re.sub(
            rf'(?<![A-Za-z0-9_]){re.escape(a)}(?![A-Za-z0-9_])',
            b,
            text,
        )

    for i, value in enumerate(third_party_urls):
        text = text.replace(f'__SILA_THIRD_URL_{i:06d}__', value)

    return restore_matches(
        text,
        protected,
        'SILA_CONTENT_PROTECTED',
    )


def transform_path(rel: str) -> str:
    text, protected = mask_matches(
        rel,
        PROTECTED_PATH,
        'SILA_PATH_PROTECTED',
    )

    text = text.replace('eip-review-bot', 'sip-review-bot')
    text = text.replace('EIP-Review-Bot', 'SIP-Review-Bot')
    text = text.replace('eipw-action', 'sipw-action')
    text = text.replace('eipw', 'sipw')
    text = text.replace('ethereumjs', 'silajs')
    text = text.replace('EthereumJS', 'SilaJS')
    text = dense_identity(text)

    path_word_rules = [
        ('ERCS', 'SRCS'), ('ERCs', 'SRCs'), ('ercs', 'srcs'),
        ('ERC', 'SRC'), ('erc', 'src'),
        ('EIPS', 'SIPS'), ('EIPs', 'SIPs'), ('eips', 'sips'),
        ('EIP', 'SIP'), ('eip', 'sip'),
        ('ETHEREUM', 'SILA'), ('Ethereum', 'Sila'), ('ethereum', 'sila'),
        ('ETH', 'SIL'), ('Eth', 'Sil'), ('eth', 'sil'),
        ('EVM', 'SVM'), ('Evm', 'Svm'), ('evm', 'svm'),
        ('Mainnet', 'SilaMainnet'), ('MAINNET', 'SILA_MAINNET'), ('mainnet', 'sila-mainnet'),
        ('Sepolia', 'SilaSepolia'), ('Holesky', 'SilaHolesky'),
        ('Deneb', 'SilaDeneb'), ('Fulu', 'SilaFulu'), ('PeerDAS', 'SilaPeerDAS'),
        ('Cancun', 'SilaCancun'), ('Shanghai', 'SilaShanghai'),
        ('Prague', 'SilaPrague'), ('Osaka', 'SilaOsaka'),
        ('Paris', 'SilaParis'), ('Amsterdam', 'SilaAmsterdam'),
        ('Kovan', 'SilaKovan'),
    ]

    for a, b in path_word_rules:
        text = re.sub(
            rf'(?<![A-Za-z0-9_]){re.escape(a)}(?![A-Za-z0-9_])',
            b,
            text,
        )

    return restore_matches(
        text,
        protected,
        'SILA_PATH_PROTECTED',
    )


def file_is_text(data: bytes) -> bool:
    if b'\x00' in data:
        return False
    try:
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False


mapped: dict[str, str] = {}
upstream_regular_files = 0
upstream_symlinks = 0
text_files = 0
binary_files = 0
transformed_text_files = 0
path_renames = 0

entries = [
    p for p in SRC.rglob('*')
    if p.name != '.git' and '.git' not in p.parts
]
entries.sort(
    key=lambda p: (
        len(p.relative_to(SRC).parts),
        str(p.relative_to(SRC)),
    )
)

for src in entries:
    rel = src.relative_to(SRC).as_posix()
    dst_rel = transform_path(rel)

    if dst_rel in mapped and mapped[dst_rel] != rel:
        raise SystemExit(
            f'PATH_COLLISION:{mapped[dst_rel]}::{rel}=>{dst_rel}'
        )

    mapped[dst_rel] = rel

    if dst_rel != rel:
        path_renames += 1

    dst = OUT / dst_rel

    if src.is_symlink():
        upstream_symlinks += 1
        dst.parent.mkdir(parents=True, exist_ok=True)
        target = os.readlink(src)
        os.symlink(transform_path(target), dst)
        continue

    if src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        continue

    upstream_regular_files += 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()

    if file_is_text(data):
        text_files += 1
        original = data.decode('utf-8')
        converted = transform_text(original)
        if converted != original:
            transformed_text_files += 1
        dst.write_bytes(converted.encode('utf-8'))
    else:
        binary_files += 1
        dst.write_bytes(data)

    try:
        shutil.copystat(src, dst, follow_symlinks=False)
    except OSError:
        pass

expected_generated = upstream_regular_files + upstream_symlinks
generated_files = sum(
    1 for p in OUT.rglob('*')
    if p.is_file() or p.is_symlink()
)

if generated_files != expected_generated:
    raise SystemExit(
        f'FILE_COUNT_MISMATCH:{generated_files}:{expected_generated}'
    )

forbidden_patterns = [
    re.compile(r'(?<![A-Za-z0-9_])(?:Ethereum|ETHEREUM|ethereum)(?![A-Za-z0-9_])'),
    re.compile(r'(?<![A-Za-z0-9_])(?:EIP|EIPs|EIPS|eip|eips)(?![A-Za-z0-9_])'),
    re.compile(r'(?<![A-Za-z0-9_])(?:ERC|ERCs|ERCS|erc|ercs)(?![A-Za-z0-9_])'),
    re.compile(r'github\.com/ethereum/'),
    re.compile(r'eips\.ethereum\.org'),
]

residuals: list[str] = []

for p in OUT.rglob('*'):
    if not p.is_file() or p.is_symlink():
        continue

    data = p.read_bytes()
    if not file_is_text(data):
        continue

    text = data.decode('utf-8')
    text, _ = mask_matches(
        text,
        PROTECTED_CONTENT,
        'SILA_SCAN_PROTECTED',
    )
    text = URL_RE.sub('__SILA_SCAN_URL__', text)

    for pat in forbidden_patterns:
        if pat.search(text):
            residuals.append(
                f'{p.relative_to(OUT).as_posix()}::{pat.pattern}'
            )
            break

for rel in mapped:
    masked, _ = mask_matches(
        rel,
        PROTECTED_PATH,
        'SILA_SCAN_PATH_PROTECTED',
    )

    if re.search(
        r'(?<![A-Za-z0-9])(?:EIP|Eip|eip|ERC|Erc|erc)(?=[A-Za-z0-9_.-])',
        masked,
    ):
        residuals.append(f'PATH_DENSE::{rel}')
        continue

    if re.search(
        r'(?<![A-Za-z0-9])(?:ETH|Eth|eth)(?=[0-9_-])',
        masked,
    ):
        residuals.append(f'PATH_ETH_DENSE::{rel}')
        continue

    if re.search(
        r'(?<![A-Za-z0-9_])(?:Ethereum|ethereum|EIP|eip|ERC|erc)(?![A-Za-z0-9_])',
        masked,
    ):
        residuals.append(f'PATH_TOKEN::{rel}')

if residuals:
    print('ACTIONABLE_RESIDUALS_BEGIN')
    for item in residuals[:300]:
        print(item)
    print('ACTIONABLE_RESIDUALS_END')
    raise SystemExit(
        f'ACTIONABLE_IDENTITY_RESIDUAL_COUNT={len(residuals)}'
    )

path_canaries = {
    '_includes/eipnums.html': '_includes/sipnums.html',
    '_includes/eiptable.html': '_includes/siptable.html',
    'assets/eip-4881/eip_4881.py': 'assets/sip-4881/sip_4881.py',
    'assets/eip-6110/eth2_ws_calc.py': 'assets/sip-6110/sil2_ws_calc.py',
    'assets/eip-712/eth_sign.png': 'assets/sip-712/sil_sign.png',
    'assets/eip-712/eth_signTypedData.png': 'assets/sip-712/sil_signTypedData.png',
    'assets/eip-7543/gasEVMPlusEmulate.go': 'assets/sip-7543/gasSVMPlusEmulate.go',
    'assets/eip-7976/eip7976_empirical_analysis.md': 'assets/sip-7976/sip7976_empirical_analysis.md',
    'assets/eip-8052/kat_ethfalcon512.rsp': 'assets/sip-8052/kat_silfalcon512.rsp',
    'assets/eip-1884/geth_processing.png': 'assets/sip-1884/geth_processing.png',
    'assets/eip-3607/geth.diff': 'assets/sip-3607/geth.diff',
}

for original, expected in path_canaries.items():
    actual = transform_path(original)
    if actual != expected:
        raise SystemExit(
            f'PATH_CANARY_FAIL:{original}:{actual}:{expected}'
        )

print(f'UPSTREAM_REGULAR_FILE_COUNT={upstream_regular_files}')
print(f'UPSTREAM_SYMLINK_COUNT={upstream_symlinks}')
print(f'GENERATED_FILE_COUNT={generated_files}')
print(f'TEXT_FILE_COUNT={text_files}')
print(f'BINARY_FILE_COUNT={binary_files}')
print(f'TRANSFORMED_TEXT_FILE_COUNT={transformed_text_files}')
print(f'PATH_RENAME_COUNT={path_renames}')
print('PATH_COLLISION_COUNT=0')
print('PATH_CANARY_FAILURE_COUNT=0')
print('ACTIONABLE_IDENTITY_RESIDUAL_COUNT=0')
print('GENERATION_GATE=PASS')
