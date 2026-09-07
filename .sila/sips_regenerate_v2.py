from __future__ import annotations

from pathlib import Path
import os
import re
import shutil
import sys

if len(sys.argv) != 3:
    raise SystemExit('USAGE: sips_regenerate_pure.py <upstream-worktree> <output-dir>')

SRC = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
if not SRC.is_dir():
    raise SystemExit(f'UPSTREAM_SOURCE_MISSING:{SRC}')
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

URL_RE = re.compile(r'https?://[^\s\)\]\}\>\"\']+')
MD_LINK_RE = re.compile(r'\[([^\]]+)\]\((https?://[^\)]+)\)')
ETH_RESEARCH_MD_RE = re.compile(r'\[([^\]]+)\]\(https?://ethresear\.ch/[^\)]+\)')
ETH_RESEARCH_FRONTMATTER_RE = re.compile(r'(?m)^discussions-to:\s*https?://ethresear\.ch/\S+\s*\n')


def case_token(token: str, upper: str, title: str, lower: str) -> str:
    if token.isupper():
        return upper
    if token[:1].isupper():
        return title
    return lower


def dense_identity(text: str) -> str:
    text = re.sub(r'(?<![A-Za-z0-9])(?:EIP|Eip|eip)(?=[A-Za-z0-9_.-])',
                  lambda m: case_token(m.group(0), 'SIP', 'Sip', 'sip'), text)
    text = re.sub(r'(?<![A-Za-z0-9])(?:ERC|Erc|erc)(?=[A-Za-z0-9_.-])',
                  lambda m: case_token(m.group(0), 'SRC', 'Src', 'src'), text)
    text = re.sub(r'(?<![A-Za-z0-9])(?:ETH|Eth|eth)(?=[0-9_-])',
                  lambda m: case_token(m.group(0), 'SIL', 'Sil', 'sil'), text)
    text = re.sub(r'(?<![A-Za-z0-9])(?:ETH|Eth|eth)(?=falcon)',
                  lambda m: case_token(m.group(0), 'SIL', 'Sil', 'sil'), text, flags=re.IGNORECASE)
    text = re.sub(r'(?<![A-Za-z0-9])(?:EVM|Evm|evm)(?=[0-9_+.-])',
                  lambda m: case_token(m.group(0), 'SVM', 'Svm', 'svm'), text)
    return text


def transform_url(url: str) -> str | None:
    lower = url.lower()
    if 'ethresear.ch/' in lower:
        return None
    # Real Sila counterparts.
    url = re.sub(r'(?i)github\.com/ethereum/go-ethereum', 'github.com/sila-chain/go-sila', url)
    url = re.sub(r'(?i)raw\.githubusercontent\.com/ethereum/go-ethereum', 'raw.githubusercontent.com/sila-chain/go-sila', url)
    url = re.sub(r'(?i)github\.com/ethereum/(?:eth2\.0-specs|eth2spec)', 'github.com/sila-chain/consensus-specs', url)
    # Old external Ethereum/EVM product provenance has no authoritative Sila repo.
    # Do not fabricate a link: keep the surrounding prose, remove only the URL.
    l2 = url.lower()
    if any(x in l2 for x in ('evmone', 'openethereum', 'ethereum.github.io/evmc', 'py-evm', 'pyethereum', 'cpp-ethereum', 'ethereumj', 'ethash', 'ethcore', 'ethcc')):
        return None
    url = re.sub(r'(?i)github\.com/ethereum/', 'github.com/sila-chain/', url)
    url = re.sub(r'(?i)raw\.githubusercontent\.com/ethereum/', 'raw.githubusercontent.com/sila-chain/', url)
    url = url.replace('eips.ethereum.org', 'sips.sila.org')
    url = url.replace('ethereum-magicians.org', 'sila-magicians.org')
    url = url.replace('ethereum.stackexchange.com', 'sila.stackexchange.com')
    url = url.replace('notes.ethereum.org', 'notes.sila.org')
    url = url.replace('blog.ethereum.org', 'blog.sila.org')
    url = url.replace('ethereum.org', 'sila.org')
    url = re.sub(r'(?i)(sips\.sila\.org)/erc(?=$|[/#?])', r'\1/src', url)
    url = dense_identity(url)
    # If a third-party URL still carries legacy chain/VM identity and there is
    # no real Sila counterpart, remove the URL rather than fabricate a target.
    if re.search(r'(?i)(ethereum|(?:^|[/_.+\-])eips?(?:[/_.+\-]|[0-9])|(?:^|[/_.+\-])ercs?(?:[/_.+\-]|[0-9])|evm|geth|eth2spec|eth_)', url):
        return None
    return url


def transform_text(text: str) -> str:
    text = text.replace('\\x19Ethereum Signed Message:', '\\x19Sila Signed Message:')
    text = ETH_RESEARCH_FRONTMATTER_RE.sub('', text)
    text = ETH_RESEARCH_MD_RE.sub(lambda m: m.group(1), text)
    text = text.replace('../assets/eip-712/eth_sign.png', '../assets/eip-712/sil_sign.png')
    text = text.replace('../assets/eip-712/eth_signTypedData.png', '../assets/eip-712/sil_signTypedData.png')

    def md_link_repl(m: re.Match[str]) -> str:
        label, url = m.group(1), m.group(2)
        transformed = transform_url(url)
        return label if transformed is None else f'[{label}]({transformed})'
    text = MD_LINK_RE.sub(md_link_repl, text)

    saved_urls: list[str] = []
    def url_repl(m: re.Match[str]) -> str:
        original = m.group(0)
        transformed = transform_url(original)
        if transformed is None:
            return ''
        if transformed != original:
            return transformed
        token = f'__SILA_URL_{len(saved_urls):06d}__'
        saved_urls.append(original)
        return token
    text = URL_RE.sub(url_repl, text)

    exact = [
        ('github.com/ethereum/go-ethereum', 'github.com/sila-chain/go-sila'),
        ('ethereum/go-ethereum', 'sila-chain/go-sila'),
        ('go-ethereum', 'go-sila'),
        ('PyEthereum', 'PySila'), ('pyethereum', 'pysila'),
        ('CPP-Ethereum', 'CPP-Sila'), ('cpp-ethereum', 'cpp-sila'),
        ('EthereumJ', 'SilaJ'), ('ethereumj', 'silaj'),
        ('ETHASH', 'SILASH'), ('Ethash', 'Silash'), ('ethash', 'silash'),
        ('ETHCORE', 'SILCORE'), ('Ethcore', 'Silcore'), ('ethcore', 'silcore'),
        ('EthCC', 'Sila community conference'),
        ('GETH_NAME', 'SILA_NAME'), ('Geth', 'Sila'), ('GETH', 'SILA'), ('geth', 'sila'),
        ('eth2.0-specs', 'consensus-specs'), ('eth2spec', 'consensus-specs'),
        ('Py-EVM', 'Py-SVM'), ('py-evm', 'py-svm'),
        ('openethereum-evm', 'sila-svm'), ('OpenEthereum', 'Sila'), ('openethereum', 'sila'),
        ('web+evm', 'web+svm'), ('EVM64', 'SVM64'), ('Evm64', 'Svm64'), ('evm64', 'svm64'),
        ('gasEVM', 'gasSVM'), ('GasEVM', 'GasSVM'), ('GASEVM', 'GASSVM'),
        ('test_setEVM', 'test_setSVM'), ('mldsa_evm', 'mldsa_svm'),
        ('evmone', 'svmone'), ('EVMONE', 'SVMONE'), ('EVMC', 'SVMC'), ('evmc', 'svmc'),
        ('eip-review-bot', 'sip-review-bot'), ('EIP-Review-Bot', 'SIP-Review-Bot'),
        ('eipw-action', 'sipw-action'), ('EIPW', 'SIPW'), ('eipw', 'sipw'),
        ('IWETH', 'IWSIL'), ('WETH','WSIL'), ('IERC', 'ISRC'), ('AERC', 'ASRC'), ('IEIP', 'ISIP'),
        ('Ethereum Foundation', 'Sila Foundation'), ('ethereum Foundation', 'Sila Foundation'),
        ('Ethereum Magicians', 'Sila Magicians'), ('Ethereum Stack Exchange', 'Sila Stack Exchange'),
        ('Ethereum Research', 'Sila Research'), ('Etherscan', 'SilaScan'), ('etherscan', 'silascan'),
        ('ethereumjs', 'silajs'), ('EthereumJS', 'SilaJS'), ('@ethereumjs', '@silajs'),
        ('/eth2/', '/sila/'), ('/eth/', '/sila/'),
    ]
    for a, b in exact:
        text = text.replace(a, b)

    text = re.sub(r'(?<![A-Za-z0-9_])eth_([A-Za-z0-9_]+)', r'sil_\1', text)
    text = re.sub(r'(?i)(?<![A-Za-z0-9_])ethereum_([A-Za-z0-9_]+)', r'sila_\1', text)
    text = re.sub(r'(?<![A-Za-z0-9_.-])ethereum/', 'sila-chain/', text)
    text = dense_identity(text)

    rules = [
        ('ERCS','SRCS'),('ERCs','SRCs'),('ercs','srcs'),('ERC','SRC'),('erc','src'),
        ('EIPS','SIPS'),('EIPs','SIPs'),('eips','sips'),('EIP','SIP'),('eip','sip'),
        ('ETHEREUM','SILA'),('Ethereum','Sila'),('ethereum','sila'),('Ether','Sila'),('ether','sila'),
        ('ETH','SIL'),('Eth','Sil'),('eth','sil'),
        ('EVM','SVM'),('Evm','Svm'),('evm','svm'),
        ('Mainnet','SilaMainnet'),('MAINNET','SILA_MAINNET'),('mainnet','sila-mainnet'),
        ('Sepolia','SilaSepolia'),('Holesky','SilaHolesky'),('Deneb','SilaDeneb'),('Fulu','SilaFulu'),('PeerDAS','SilaPeerDAS'),
        ('Cancun','SilaCancun'),('Shanghai','SilaShanghai'),('Prague','SilaPrague'),('Osaka','SilaOsaka'),
        ('Paris','SilaParis'),('Amsterdam','SilaAmsterdam'),('Kovan','SilaKovan'),
    ]
    for a, b in rules:
        text = re.sub(rf'(?<![A-Za-z0-9_]){re.escape(a)}(?![A-Za-z0-9_])', b, text)

    text = re.sub(r'(?i)evm', 'SVM', text)
    for i, value in enumerate(saved_urls):
        text = text.replace(f'__SILA_URL_{i:06d}__', value)
    return text


def transform_path(rel: str) -> str:
    replacements = [
        ('go-ethereum','go-sila'),('GETH','SILA'),('Geth','Sila'),('geth','sila'),
        ('PyEthereum','PySila'),('pyethereum','pysila'),('CPP-Ethereum','CPP-Sila'),('cpp-ethereum','cpp-sila'),
        ('EthereumJ','SilaJ'),('ethereumj','silaj'),('ETHASH','SILASH'),('Ethash','Silash'),('ethash','silash'),
        ('ETHCORE','SILCORE'),('Ethcore','Silcore'),('ethcore','silcore'),
        ('eth2.0-specs','consensus-specs'),('eth2spec','consensus-specs'),
        ('Py-EVM','Py-SVM'),('py-evm','py-svm'),('openethereum-evm','sila-svm'),
        ('web+evm','web+svm'),('EVM64','SVM64'),('evm64','svm64'),('gasEVM','gasSVM'),
        ('test_setEVM','test_setSVM'),('mldsa_evm','mldsa_svm'),('evmone','svmone'),('EVMC','SVMC'),('evmc','svmc'),
        ('eip-review-bot','sip-review-bot'),('EIP-Review-Bot','SIP-Review-Bot'),('eipw-action','sipw-action'),('eipw','sipw'),
        ('ethereumjs','silajs'),('EthereumJS','SilaJS'),('IWETH','IWSIL'),('WETH','WSIL'),('IERC','ISRC'),('AERC','ASRC'),('IEIP','ISIP'),
    ]
    text = rel
    for a,b in replacements:
        text = text.replace(a,b)
    text = re.sub(r'(?<![A-Za-z0-9_])eth_([A-Za-z0-9_]+)', r'sil_\1', text)
    text = re.sub(r'(?i)(?<![A-Za-z0-9_])ethereum_([A-Za-z0-9_]+)', r'sila_\1', text)
    text = dense_identity(text)
    rules = [
        ('ERCS','SRCS'),('ERCs','SRCs'),('ercs','srcs'),('ERC','SRC'),('erc','src'),
        ('EIPS','SIPS'),('EIPs','SIPs'),('eips','sips'),('EIP','SIP'),('eip','sip'),
        ('ETHEREUM','SILA'),('Ethereum','Sila'),('ethereum','sila'),('ETH','SIL'),('Eth','Sil'),('eth','sil'),
        ('EVM','SVM'),('Evm','Svm'),('evm','svm'),
        ('Mainnet','SilaMainnet'),('MAINNET','SILA_MAINNET'),('mainnet','sila-mainnet'),
        ('Sepolia','SilaSepolia'),('Holesky','SilaHolesky'),('Deneb','SilaDeneb'),('Fulu','SilaFulu'),('PeerDAS','SilaPeerDAS'),
        ('Cancun','SilaCancun'),('Shanghai','SilaShanghai'),('Prague','SilaPrague'),('Osaka','SilaOsaka'),
        ('Paris','SilaParis'),('Amsterdam','SilaAmsterdam'),('Kovan','SilaKovan'),
    ]
    for a,b in rules:
        text = re.sub(rf'(?<![A-Za-z0-9_]){re.escape(a)}(?![A-Za-z0-9_])', b, text)
    text = re.sub(r'(?i)evm', 'SVM', text)
    return text


def is_text(data: bytes) -> bool:
    if b'\x00' in data:
        return False
    try:
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

mapped: dict[str,str] = {}
regular = symlinks = text_count = binary_count = changed_text = path_renames = 0
entries = [p for p in SRC.rglob('*') if p.name != '.git' and '.git' not in p.parts]
entries.sort(key=lambda p:(len(p.relative_to(SRC).parts), str(p.relative_to(SRC))))
for src in entries:
    rel = src.relative_to(SRC).as_posix()
    dst_rel = transform_path(rel)
    if dst_rel in mapped and mapped[dst_rel] != rel:
        raise SystemExit(f'PATH_COLLISION:{mapped[dst_rel]}::{rel}=>{dst_rel}')
    mapped[dst_rel] = rel
    path_renames += int(dst_rel != rel)
    dst = OUT / dst_rel
    if src.is_symlink():
        symlinks += 1
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(transform_path(os.readlink(src)), dst)
    elif src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
    else:
        regular += 1
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        if is_text(data):
            text_count += 1
            s = data.decode('utf-8')
            t = transform_text(s)
            changed_text += int(t != s)
            dst.write_text(t, encoding='utf-8')
        else:
            binary_count += 1
            dst.write_bytes(data)
        try:
            shutil.copystat(src,dst,follow_symlinks=False)
        except OSError:
            pass

generated = sum(1 for p in OUT.rglob('*') if p.is_file() or p.is_symlink())
if generated != regular + symlinks:
    raise SystemExit(f'FILE_COUNT_MISMATCH:{generated}:{regular+symlinks}')

# Absolute pure-Sila identity gate. These forms were protected by the old policy;
# under the pure policy they are now actionable failures everywhere in generated text/path names.
forbidden = [
    r'(?<![A-Za-z0-9_])(?:Ethereum|ETHEREUM|ethereum)(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])(?:EIP|EIPs|EIPS|eip|eips)(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])(?:ERC|ERCs|ERCS|erc|ercs)(?![A-Za-z0-9_])',
    r'github\.com/ethereum/', r'eips\.ethereum\.org', r'ethresear\.ch/',
    r'(?<![A-Za-z0-9_])go-ethereum(?![A-Za-z0-9_])', r'(?<![A-Za-z0-9_])(?:geth|Geth|GETH)(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])eth_[A-Za-z0-9_]+', r'eth2spec', r'eth2\.0-specs',
    r'Py-EVM', r'py-evm', r'openethereum-evm', r'web\+evm', r'(?<![A-Za-z0-9_])EVMC(?![A-Za-z0-9_])',
    r'(?<![A-Za-z0-9_])evmone(?![A-Za-z0-9_])', r'(?<![A-Za-z0-9_])EVM[0-9]+', r'gasEVM', r'mldsa_evm', r'test_setEVM',
    r'(?<![A-Za-z0-9_])(?:EVM|Evm|evm)(?![A-Za-z0-9_])',
    r'(?i)(?<![A-Za-z0-9_])ethereum_[A-Za-z0-9_]+',
    r'(?i)(?<![A-Za-z0-9_])pyethereum(?![A-Za-z0-9_])',
    r'(?i)(?<![A-Za-z0-9_])cpp-ethereum(?![A-Za-z0-9_])',
    r'(?i)(?<![A-Za-z0-9_])ethereumj(?![A-Za-z0-9_])',
    r'(?i)(?<![A-Za-z0-9_])ethash(?![A-Za-z0-9_])',
    r'(?i)(?<![A-Za-z0-9_])ethcore(?![A-Za-z0-9_])',
    r'(?i)(?<![A-Za-z0-9_])ethfalcon[A-Za-z0-9_]*',
    r'(?<![A-Za-z0-9_])EthCC(?![A-Za-z0-9_])',
    r'(?i)evm',
]
forbidden_rx=[re.compile(x) for x in forbidden]
residuals=[]
for p in OUT.rglob('*'):
    rel=p.relative_to(OUT).as_posix()
    for rx in forbidden_rx:
        if rx.search(rel):
            residuals.append(f'PATH::{rel}::{rx.pattern}'); break
    if p.is_file() and not p.is_symlink():
        data=p.read_bytes()
        if is_text(data):
            txt=data.decode('utf-8')
            for rx in forbidden_rx:
                if rx.search(txt):
                    residuals.append(f'TEXT::{rel}::{rx.pattern}'); break
if residuals:
    print('PURE_SILA_RESIDUALS_BEGIN')
    print('\n'.join(residuals[:500]))
    print('PURE_SILA_RESIDUALS_END')
    raise SystemExit(f'PURE_SILA_IDENTITY_RESIDUAL_COUNT={len(residuals)}')

path_canaries={
    'assets/eip-1884/geth_processing.png':'assets/sip-1884/sila_processing.png',
    'assets/eip-3607/geth.diff':'assets/sip-3607/sila.diff',
    'assets/eip-7543/gasEVMPlusEmulate.go':'assets/sip-7543/gasSVMPlusEmulate.go',
    'assets/eip-7979/riscv/evm64.py':'assets/sip-7979/riscv/svm64.py',
    'assets/eip-8051/mldsa_evm.rsp':'assets/sip-8051/mldsa_svm.rsp',
    'assets/eip-8052/kat_ethfalcon512.rsp':'assets/sip-8052/kat_silfalcon512.rsp',
    'assets/eip-712/eth_sign.png':'assets/sip-712/sil_sign.png',
    'assets/eip-712/eth_signTypedData.png':'assets/sip-712/sil_signTypedData.png',
}
for old,new in path_canaries.items():
    got=transform_path(old)
    if got != new:
        raise SystemExit(f'PATH_CANARY_FAIL:{old}:{got}:{new}')
semantic_canaries={
    'eth_getBalance':'sil_getBalance','GETH_NAME':'SILA_NAME','Geth client':'Sila client','go-ethereum':'go-sila',
    'Py-EVM':'Py-SVM','EVMC_CALL':'SVMC_CALL','evmone':'svmone','EVM64':'SVM64','gasEVMPlusDECADD':'gasSVMPlusDECADD',
    'web+evm':'web+svm','the EVM executes':'the SVM executes','\\x19Ethereum Signed Message:':'\\x19Sila Signed Message:',
    'ethereum_best_known_block_number':'sila_best_known_block_number','PyEthereum':'PySila','ethash':'silash','ethcore':'silcore','EthCC':'Sila community conference',
    'ethfalcon512':'silfalcon512',
}
for old,new in semantic_canaries.items():
    got=transform_text(old)
    if got != new:
        raise SystemExit(f'SEMANTIC_CANARY_FAIL:{old}:{got}:{new}')

print(f'UPSTREAM_REGULAR_FILE_COUNT={regular}')
print(f'UPSTREAM_SYMLINK_COUNT={symlinks}')
print(f'GENERATED_FILE_COUNT={generated}')
print(f'TEXT_FILE_COUNT={text_count}')
print(f'BINARY_FILE_COUNT={binary_count}')
print(f'TRANSFORMED_TEXT_FILE_COUNT={changed_text}')
print(f'PATH_RENAME_COUNT={path_renames}')
print('PATH_COLLISION_COUNT=0')
print('PATH_CANARY_FAILURE_COUNT=0')
print('SEMANTIC_CANARY_FAILURE_COUNT=0')
print('PURE_SILA_IDENTITY_RESIDUAL_COUNT=0')
print('ACTIONABLE_IDENTITY_RESIDUAL_COUNT=0')
print('PURE_SILA_GENERATION_GATE=PASS')
print('GENERATION_GATE=PASS')
