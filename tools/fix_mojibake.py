# Repair UTF-8-as-GBK mojibake in wiki templates.
# Corruption: UTF-8 bytes decoded as GBK; invalid GBK pairs became literal '?'
# (eating the GBK lead byte AND one ASCII trail byte < 0x40).
import glob
import re
import sys

RUN = re.compile(r'[^\x00-\x7F?]+\?*')

# context-keyed overrides for '?' spots where the eaten byte is a digit
OVERRIDES = {
    'Stages 1鈥? from': 'Stages 1–2 from',
    'Stages 3鈥? at': 'Stages 3–5 at',
    '馃': '🤝',
}

EXTRA_OK = set('×·—–→←↑↓…’‘“”±γβαμ')


def plausible(s):
    for ch in s:
        o = ord(ch)
        if o < 0x80 or ch in EXTRA_OK:
            continue
        if 0x4E00 <= o <= 0x9FFF:      # CJK
            continue
        if 0x2000 <= o <= 0x206F:      # general punctuation
            continue
        if 0x2460 <= o <= 0x24FF:      # enclosed numerics ①②③
            continue
        if 0x1F000 <= o <= 0x1FAFF or 0x2600 <= o <= 0x27BF:  # emoji/symbols
            continue
        return False
    return True


def recover(run, next_ch):
    q = len(run) - len(run.rstrip('?'))
    base = run.rstrip('?')
    try:
        b = base.encode('gbk')
    except UnicodeEncodeError:
        return None
    if q == 0:
        try:
            out = b.decode('utf-8')
        except UnicodeDecodeError:
            return None
        return out if plausible(out) else None
    if q != 1:
        return None
    cands = []
    if b.endswith(b'\xe2\x86'):        # arrow prefix: →
        cands = [(0x92, 0x3C if next_ch == '/' else 0x20)]
    elif b.endswith(b'\xe2\x80'):      # dash prefix: em dash + space
        cands = [(0x94, 0x20), (0x93, 0x20)]
    for c in cands:
        try:
            out = (b + bytes(c)).decode('utf-8')
        except UnicodeDecodeError:
            continue
        if plausible(out):
            return out
    return None


def fix_text(t):
    for old, new in OVERRIDES.items():
        t = t.replace(old, new)

    def repl(m):
        nxt = t[m.end()] if m.end() < len(t) else ''
        return recover(m.group(0), nxt) or m.group(0)

    return RUN.sub(repl, t)


def main(apply=False):
    for f in sorted(glob.glob('wiki/**/*.html', recursive=True) +
                    glob.glob('static/**/*.css', recursive=True) +
                    glob.glob('static/**/*.js', recursive=True)):
        t = open(f, encoding='utf-8').read()
        fixed = fix_text(t)
        if fixed == t:
            continue
        if apply:
            open(f, 'w', encoding='utf-8', newline='').write(fixed)
            print('FIXED', f)
        else:
            for m in RUN.finditer(t):
                old = m.group(0)
                nxt = t[m.end()] if m.end() < len(t) else ''
                new = recover(old, nxt)
                if new and new != old:
                    s = max(0, m.start() - 40)
                    ctx_old = t[s:m.end() + 20].replace('\n', ' ')
                    ctx_new = fix_text(t[s:m.end() + 20]).replace('\n', ' ')
                    print(f'{f}\n  OLD {ctx_old}\n  NEW {ctx_new}')


if __name__ == '__main__':
    main(apply='--apply' in sys.argv)
