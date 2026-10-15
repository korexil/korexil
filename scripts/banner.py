"""Draw the profile banner for the current moment: today's moon phase, and the
shiba asleep at night in Japan. Writes assets/banner-dark.svg and banner-light.svg.

    python scripts/banner.py                      # now
    python scripts/banner.py --at 2026-10-21T02:00+09:00 --out preview/
"""
import argparse
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
SYNODIC = 29.530588853
NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)

PALETTES = {
    'dark': dict(bg='#0d1117', border='#30363d', text='#e6edf3', muted='#8b949e', say='#c9d1d9',
                 panel='#161b22', moon='#fbefc0', shadow='#000000', shadow_op=0.35,
                 llm='#58a6ff', tts='#f0b429', wave='#3fb950'),
    'light': dict(bg='#ffffff', border='#d0d7de', text='#1f2328', muted='#59636e', say='#1f2328',
                  panel='#f6f8fa', moon='#d4a72c', shadow='#1f2328', shadow_op=0.12,
                  llm='#0969da', tts='#bf8700', wave='#1a7f37'),
}

FUR, CREAM, INK = '#e9a15b', '#fff1dc', '#2b1d14'


def moon_phase(t):
    """Fraction of the synodic month: 0 new, 0.5 full."""
    return ((t - NEW_MOON).total_seconds() / 86400 / SYNODIC) % 1.0


def moon_path(cx, cy, r, f):
    """Lit part of the moon as seen from the northern hemisphere."""
    k = (1 - math.cos(2 * math.pi * f)) / 2          # illuminated fraction
    rx = r * abs(math.cos(2 * math.pi * f))          # terminator half-width
    waxing = f < 0.5
    limb = 1 if waxing else 0                        # right limb when waxing
    if waxing:
        term = 0 if k < 0.5 else 1
    else:
        term = 1 if k < 0.5 else 0
    top, bottom = f'{cx} {cy - r}', f'{cx} {cy + r}'
    return f'M{top} A{r} {r} 0 0 {limb} {bottom} A{rx:.2f} {r} 0 0 {term} {top} Z'


def asleep(t):
    h = t.astimezone(JST).hour
    return h >= 23 or h < 7


def bars(color):
    durs = [.9, .7, 1.1, .8, .6, 1, .75, .95, .65, 1.15, .85, .7, 1.05, .8, .6, .95, .75, 1.1, .7, .9, .65, 1, .8, .7, 1.05, .85]
    dels = [.1, .5, .3, .7, .2, .9, .4, .6, .15, .8, .35, .55, .25, .65, .45, .05, .85, .3, .6, .2, .75, .4, .1, .5, .7, .35]
    out = [f'    <g fill="{color}">']
    for i, (d, dl) in enumerate(zip(durs, dels)):
        out.append(f'      <rect class="bar grow" x="{i * 8}" y="-30" width="5" height="60" rx="2.5" '
                   f'style="animation-duration:{d}s;animation-delay:-{dl}s"/>')
    out.append('    </g>')
    return '\n'.join(out)


def shiba(p, sleeping):
    base = f'stroke="{INK}" stroke-linejoin="round" stroke-linecap="round"'
    ln = base + ' stroke-width="3"'
    thin = base + ' stroke-width="2.5"'
    if sleeping:
        eyes = (f'  <path d="M160 100 Q166 105 172 100" fill="none" {thin}/>\n'
                f'  <path d="M192 100 Q198 105 204 100" fill="none" {thin}/>')
        mouth = ''
        extra = (f'  <g fill="{p["muted"]}" font-weight="600">\n'
                 f'    <text class="z" x="226" y="78" font-size="14">z</text>\n'
                 f'    <text class="z z2" x="236" y="62" font-size="18">z</text>\n'
                 f'    <text class="z z3" x="248" y="44" font-size="22">Z</text>\n'
                 f'  </g>\n'
                 f'  <text x="38" y="24" fill="{p["muted"]}" font-size="12">おやすみ中</text>')
        lines = ['すやすや…']
        tail_cls, ear_cls, breath = 'tail-still', '', 'breath slow'
    else:
        eyes = (f'  <ellipse class="eye grow" cx="166" cy="99" rx="5" ry="5.5" fill="{INK}"/>\n'
                f'  <ellipse class="eye grow" cx="198" cy="99" rx="5" ry="5.5" fill="{INK}"/>')
        mouth = (f'  <ellipse class="tongue" cx="182" cy="125" rx="5" ry="4.5" fill="#e0533d" '
                 f'style="transform-box:fill-box;transform-origin:50% 0%"/>\n')
        extra = (f'  <g fill="none" stroke="{p["say"]}" stroke-width="2.5" stroke-linecap="round">\n'
                 f'    <path class="sw" d="M232 104 Q238 114 232 124"/>\n'
                 f'    <path class="sw sw2" d="M241 98 Q250 114 241 130"/>\n'
                 f'  </g>')
        lines = ['おはよう！', 'お茶、もう一杯どう？', '今日はいい天気だね']
        tail_cls, ear_cls, breath = 'tail', 'ear', 'breath'

    if len(lines) == 1:
        says = f'  <text x="130" y="228" text-anchor="middle" fill="{p["say"]}" font-size="18">{lines[0]}</text>'
    else:
        says = '\n'.join(
            f'  <text class="say{"" if i == 0 else f" say{i + 1}"}" x="130" y="228" text-anchor="middle" '
            f'fill="{p["say"]}" font-size="18">{s}</text>' for i, s in enumerate(lines))

    return f'''  <ellipse cx="134" cy="192" rx="92" ry="7" fill="{p["shadow"]}" opacity="{p["shadow_op"]}"/>
  <g class="{tail_cls}">
    <circle cx="66" cy="112" r="17" fill="{FUR}" {ln}/>
    <circle cx="68" cy="110" r="7" fill="{CREAM}"/>
  </g>
  <g class="{breath}">
    <rect x="40" y="112" width="160" height="76" rx="38" fill="{FUR}" {ln}/>
    <rect x="66" y="160" width="104" height="24" rx="12" fill="{CREAM}"/>
  </g>
  <ellipse cx="146" cy="186" rx="13" ry="7" fill="{CREAM}" {ln}/>
  <ellipse cx="174" cy="186" rx="13" ry="7" fill="{CREAM}" {ln}/>
  <g class="{ear_cls}">
    <path d="M146 80 L153 42 L178 66 Z" fill="{FUR}" {ln}/>
    <path d="M153 70 L156 52 L168 64 Z" fill="{CREAM}"/>
  </g>
  <path d="M186 66 L211 42 L216 80 Z" fill="{FUR}" {ln}/>
  <path d="M196 64 L208 52 L210 70 Z" fill="{CREAM}"/>
  <circle cx="181" cy="104" r="44" fill="{FUR}" {ln}/>
  <ellipse cx="183" cy="122" rx="33" ry="22" fill="{CREAM}"/>
  <ellipse cx="166" cy="84" rx="5" ry="3.5" fill="{CREAM}"/>
  <ellipse cx="198" cy="84" rx="5" ry="3.5" fill="{CREAM}"/>
{eyes}
  <ellipse cx="155" cy="117" rx="7" ry="4" fill="#f28b82" opacity="0.5"/>
  <ellipse cx="210" cy="117" rx="7" ry="4" fill="#f28b82" opacity="0.5"/>
  <ellipse cx="182" cy="112" rx="5.5" ry="3.8" fill="{INK}"/>
{mouth}  <path d="M175 118 Q178.5 123 182 118 Q185.5 123 189 118" fill="none" {thin}/>
{extra}
{says}'''


def banner(theme, t):
    p = PALETTES[theme]
    # the moon is drawn for noon JST of the day, so the file only changes at sleep/wake and once a day
    day = t.astimezone(JST).replace(hour=12, minute=0, second=0, microsecond=0)
    f = moon_phase(day)
    sleeping = asleep(t)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="250" viewBox="0 0 860 250" role="img" aria-label="A shiba plush {'asleep' if sleeping else 'talking'} while a local LLM and TTS take turns on one 8 GB GPU">
  <style>
    text {{ font-family: "Segoe UI", "Hiragino Sans", "Noto Sans JP", "Yu Gothic UI", sans-serif; }}
    .muted {{ fill: {p["muted"]}; font-size: 16px; }}
    .big {{ fill: {p["text"]}; font-size: 20px; font-weight: 600; }}
    .grow {{ transform-box: fill-box; transform-origin: center; }}
    .eye {{ animation: blink 4.2s infinite; }}
    @keyframes blink {{ 0%, 90%, 100% {{ transform: scaleY(1); }} 94% {{ transform: scaleY(0.1); }} }}
    .tongue {{ animation: talk 0.5s infinite alternate ease-in-out; }}
    @keyframes talk {{ from {{ transform: scaleY(0.3); }} to {{ transform: scaleY(1); }} }}
    .tail {{ transform-box: fill-box; transform-origin: 70% 100%; animation: wag 0.9s infinite alternate ease-in-out; }}
    @keyframes wag {{ from {{ transform: rotate(-10deg); }} to {{ transform: rotate(10deg); }} }}
    .ear {{ transform-box: fill-box; transform-origin: 50% 100%; animation: twitch 5s infinite; }}
    @keyframes twitch {{ 0%, 80%, 100% {{ transform: rotate(0); }} 84% {{ transform: rotate(9deg); }} 88% {{ transform: rotate(-3deg); }} }}
    .breath {{ transform-box: fill-box; transform-origin: 50% 100%; animation: breath 3.2s infinite ease-in-out; }}
    .breath.slow {{ animation-duration: 5s; }}
    @keyframes breath {{ 0%, 100% {{ transform: scaleY(1); }} 50% {{ transform: scaleY(1.03); }} }}
    .sw {{ opacity: 0; animation: sw 1.2s infinite; }}
    .sw2 {{ animation-delay: 0.3s; }}
    @keyframes sw {{ 0% {{ opacity: 0; }} 30% {{ opacity: 1; }} 70%, 100% {{ opacity: 0; }} }}
    .z {{ opacity: 0; animation: z 3s infinite; animation-delay: -1.2s; }}
    .z2 {{ animation-delay: -2.2s; }}
    .z3 {{ animation-delay: -0.2s; }}
    @keyframes z {{ 0% {{ opacity: 0; transform: translateY(6px); }} 30%, 70% {{ opacity: 1; }} 100% {{ opacity: 0; transform: translateY(-6px); }} }}
    .llm {{ animation: llm 2.4s infinite; }}
    .tts {{ animation: tts 2.4s infinite; }}
    @keyframes llm {{ 0%, 42% {{ opacity: 1; }} 50%, 92% {{ opacity: 0.35; }} 100% {{ opacity: 1; }} }}
    @keyframes tts {{ 0%, 42% {{ opacity: 0.35; }} 50%, 92% {{ opacity: 1; }} 100% {{ opacity: 0.35; }} }}
    .bar {{ animation: wave 1s infinite alternate ease-in-out; }}
    @keyframes wave {{ from {{ transform: scaleY(0.15); }} to {{ transform: scaleY(1); }} }}
    .say {{ opacity: 0; animation: say 9s infinite; animation-delay: -1s; }}
    .say2 {{ animation-delay: 2s; }}
    .say3 {{ animation-delay: 5s; }}
    @keyframes say {{ 0% {{ opacity: 0; }} 4%, 30% {{ opacity: 1; }} 34%, 100% {{ opacity: 0; }} }}
  </style>

  <rect x="0.5" y="0.5" width="859" height="249" rx="16" fill="{p["bg"]}" stroke="{p["border"]}"/>

  <!-- moon, phase of {t.astimezone(JST):%Y-%m-%d} (age {f * SYNODIC:.1f} days) -->
  <circle cx="58" cy="54" r="20" fill="{p["moon"]}" opacity="0.15"/>
  <path d="{moon_path(58, 54, 20, f)}" fill="{p["moon"]}"/>

{shiba(p, sleeping)}

  <g transform="translate(276 36)">
    <text class="big" x="0" y="20">8 GB GPU · two models</text>
    <text class="muted" x="5" y="54">LLM 2.8 GB</text>
    <text class="muted" x="114" y="54">TTS 4.0 GB</text>
    <rect x="0" y="62" width="300" height="40" rx="9" fill="{p["panel"]}" stroke="{p["border"]}"/>
    <rect class="llm" x="5" y="67" width="105" height="30" rx="6" fill="{p["llm"]}"/>
    <rect class="tts" x="114" y="67" width="150" height="30" rx="6" fill="{p["tts"]}"/>
    <text class="muted" x="0" y="132">take turns, one sentence at a time</text>
  </g>

  <g transform="translate(612 104)">
{bars(p["wave"])}
    <text class="muted" x="0" y="60">playback never stops</text>
    <text class="big" x="0" y="88">gaps 4.22 s → 0.17 s</text>
  </g>
</svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--at', help='ISO time to draw instead of now')
    ap.add_argument('--out', default='assets')
    args = ap.parse_args()
    t = datetime.fromisoformat(args.at) if args.at else datetime.now(timezone.utc)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme in PALETTES:
        (out / f'banner-{theme}.svg').write_text(banner(theme, t), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
