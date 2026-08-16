# -*- coding: utf-8 -*-
"""테오화랑 정적 사이트 생성기 — content/*.json 을 읽어 dist/ 를 만듭니다."""
import json, os, glob, shutil, re, html
from PIL import Image

SRC_IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
WIDTHS  = [400, 800, 1400]
_cache  = {}

def derive(src):
    """원본 1장 → 여러 폭으로 생성하고 srcset 문자열을 돌려준다."""
    if src in _cache: return _cache[src]
    rel = src.lstrip('/').replace('images/','',1)
    ap  = os.path.join(SRC_IMG, rel)
    if not os.path.exists(ap):
        _cache[src]=(src,'',0,0); return _cache[src]
    im = Image.open(ap); W,H = im.size
    base,ext = os.path.splitext(rel)
    outs=[]
    for w in WIDTHS:
        if w > W and outs: break
        w = min(w, W)
        o = f'{base}-{w}.jpg'
        op = os.path.join(OUT,'images',o)
        os.makedirs(os.path.dirname(op), exist_ok=True)
        if not os.path.exists(op):
            im2 = im.copy(); im2.thumbnail((w, w*4), Image.LANCZOS)
            im2.convert('RGB').save(op, 'JPEG', quality=80, optimize=True, progressive=True)
        outs.append((w, '/images/'+o))
        if w >= W: break
    srcset = ', '.join(f'{u} {w}w' for w,u in outs)
    fallback = outs[min(1,len(outs)-1)][1]
    _cache[src] = (fallback, srcset, W, H)
    return _cache[src]

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, '..', 'dist')
def load(p): return json.load(open(os.path.join(ROOT,'content',p), encoding='utf-8'))

SITE   = load('site.json')
ABOUT  = load('about.json')
GUIDE  = load('guide.json')
RENTAL = load('rental.json')
EXH    = sorted([json.load(open(f,encoding='utf-8')) for f in glob.glob(ROOT+'/content/exhibitions/*.json')],
                key=lambda e: e['start'], reverse=True)
ART    = sorted([json.load(open(f,encoding='utf-8')) for f in glob.glob(ROOT+'/content/artists/*.json')],
                key=lambda a: a['order'])
BYSLUG = {a['slug']: a for a in ART}
LIVE   = [e for e in EXH if not e.get('stub')]

TYPE = {'solo':'Solo','duo':'Duo','group':'Group'}
def fdate(s):
    if not s: return ''
    y,m,d = s.split('-'); return f"{y}. {int(m)}. {int(d)}"
def period(e):
    a=fdate(e['start']); b=fdate(e.get('end') or '')
    if not b: return a
    ys,ms,_=e['start'].split('-'); ye,me,de=e['end'].split('-')
    return f"{a} — {b}" if ys!=ye else f"{a} — {int(me)}. {int(de)}"

LOGO = open(os.path.join(ROOT,'logo_symbol.html'), encoding='utf-8').read()

def img(src, ratio=None, pos='center', alt='', cls='', lazy=True, ph='', sizes='100vw'):
    st = f' style="aspect-ratio:{ratio}"' if ratio else ''
    if not src:
        return f'<div class="ph {cls}"{st} data-ph="{ph}"></div>'
    best, srcset, W, H = derive(src)
    lz = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    ss = f' srcset="{srcset}" sizes="{sizes}"' if srcset else ''
    wh = f' width="{W}" height="{H}"' if W else ''
    return (f'<div class="ph hasim {cls}"{st}>'
            f'<img class="im" src="{best}"{ss}{wh} alt="{html.escape(alt)}"{lz} '
            f'style="object-position:{pos}"></div>')

def head(title, desc, canonical):
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#1B2166">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/assets/favicon.svg">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;500;600;700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<svg style="display:none">{LOGO}</svg>
'''

def header(active=''):
    items=''
    for slug,ko,en in SITE['nav']:
        cls=' class="active"' if slug==active else ''
        items+=f'    <a href="/{slug}/"{cls} data-ko="{ko}" data-en="{en}">{ko} <em>{en}</em></a>\n'
    return f'''<header>
  <div class="util"><span>TEL {SITE['tel']}</span>
    <span><button id="ko" class="on">KO</button> / <button id="en">EN</button></span></div>
  <div class="bar">
    <a href="/" class="logo"><svg><use href="#mark"/></svg><span class="txt" id="logoTxt">테오화랑</span></a>
    <button class="burger" id="burger" aria-label="메뉴"><i></i><i></i><i></i></button>
  </div>
  <nav class="panel" id="panel">
{items}  </nav>
</header>
<main>
'''

FOOT = f'''</main>
<footer class="site">
  <div class="fw">
    <div><div class="fl"><svg><use href="#mark"/></svg><b>TVG</b></div>테오화랑 · {SITE['full_en']}</div>
    <div>{SITE['address_ko']}<br>{SITE['hours']} · {SITE['closed']} 휴관</div>
    <div>TEL {SITE['tel']} &nbsp; MAIL {SITE['email']} &nbsp; {SITE['instagram']}<br>
      <span style="color:var(--faint)">© 2026 TVG</span></div>
  </div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>'''

def write(path, title, desc, body, active=''):
    d=os.path.join(OUT, path.strip('/'))
    os.makedirs(d, exist_ok=True)
    url='https://tvg.example/'+path.strip('/')+('/' if path.strip('/') else '')
    open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(
        head(title,desc,url)+header(active)+body+FOOT)

# ─────────────────────────── 부품
def exh_card(e):
    href=f"/exhibitions/{e['slug']}/"
    hero=e.get('hero') or {}
    thumb=img(hero.get('src'), '4/3', hero.get('pos','center 40%'), e['title_ko'], ph='',
              sizes='(min-width:1000px) 460px, (min-width:700px) 33vw, 110px')
    y,m,_=e['start'].split('-')
    return (f'<a href="{href}" class="exh-card">{thumb}<div>'
            f'<div class="tag">{y}. {int(m)}</div><h3>{e["title_ko"]}</h3>'
            f'<div class="sub">{e.get("subtitle_ko") or ""}</div></div></a>')

def art_card(a):
    return (f'<a href="/artists/{a["slug"]}/" class="art-card">'
            f'{img(a.get("portrait"),"3/4",a.get("portrait_pos","center 28%"),a["name_ko"],ph="인물",sizes="(min-width:700px) 25vw, 50vw")}'
            f'<div class="kn">{a["name_ko"]}</div><div class="en">{a["name_en"]}</div>'
            f'<div class="yr">b. {a["born"] or "19··"}</div></a>')

def works_grid(works):
    out='<div class="works">'
    for i,w in enumerate(works):
        cap=f'<b>{w.get("artist","")+" " if w.get("artist") else ""}《{w["title"]}》, {w["year"]}</b>'
        if w.get('medium'): cap+=w['medium']+'<br>'
        if w.get('size'):   cap+=w['size']+'<br>'
        if w.get('collection'): cap+=f'<span class="coll">{w["collection"]}</span><br>'
        cap+='<a href="/contact/" class="inq">문의하기</a>'
        out+=f'<div class="work">{img(w.get("image"),"4/5","center",w["title"],cls="bcd"[i%3],ph="작품")}<div class="cap">{cap}</div></div>'
    return out+'</div>'

def tbl(rows):
    return '<div class="tbl">'+''.join(
        f'<div class="r"><div class="k">{k}</div><div class="v">{v}</div></div>' for k,v in rows)+'</div>'

# ─────────────────────────── 페이지
def page_home():
    st=SITE.get('state','none'); cur=LIVE[0] if LIVE else None
    if st=='none':
        hero=f'''<div class="notice"><span class="nbadge">준비 중</span>
    <span>다음 전시를 준비하고 있습니다. 일정이 정해지면 이곳과 <b>인스타그램</b>에 안내드립니다.</span></div>
  <div class="prep">
    <svg class="jar" viewBox="0 0 240 244" role="img" aria-label="달항아리">{JARPATH}</svg>
    <div class="prep-txt">다음 전시를 준비하고 있습니다</div>
    <div class="prep-sub">NEXT EXHIBITION IN PREPARATION</div>
    <div class="btn2" style="justify-content:center">
      <a href="/exhibitions/" class="more">지난 전시</a><a href="/artists/" class="more">작가</a></div>
  </div>'''
    else:
        h=cur['hero'] or {}
        hero=f'''<div class="hero">{img(h.get('src'),None,h.get('pos','center 62%'),cur['title_ko'],lazy=False)}
    <div class="hero-meta wide"><div class="status">Current Exhibition</div>
      <h1 class="exh">{cur['title_ko']}</h1>
      <div class="who">{cur.get('subtitle_ko','')}<br>{period(cur)}</div>
      <a href="/exhibitions/{cur['slug']}/" class="more mt">전시 보기</a></div></div>'''
    arts=''.join(art_card(a) for a in ART[:4])
    cards=''.join(exh_card(e) for e in LIVE[:3])
    body=f'''<div class="home{' st-none' if st=='none' else ''}">
  <div class="h-wrap">{hero}</div>
  <section class="block wide sec-art">
    <div class="head-row"><span class="eyebrow">Artists</span><a href="/artists/" class="more">전체</a></div>
    <div class="art-grid">{arts}</div>
  </section>
  <section class="block wide sec-exh">
    <div class="head-row"><span class="eyebrow">Exhibitions</span><a href="/exhibitions/" class="more">전체</a></div>
    <div class="exh-grid">{cards}</div>
  </section>
  <section class="block tight mid sec-about">
    <span class="eyebrow">About</span>
    <p class="lead">{ABOUT['paras'][0].split('이러한 화랑명')[0].strip()}</p>
    <a href="/about/" class="more mt">화랑 소개</a>
  </section>
  <section class="block wide sec-visit">
    <span class="eyebrow">Visit</span>
    {tbl([('주소',SITE['address_ko']),('시간',SITE['hours']),('휴관',SITE['closed']),('관람료',SITE['admission'])])}
    <a href="/visit/" class="more mt">오시는 길</a>
  </section>
</div>'''
    write('', '테오화랑 TVG', f"테오화랑 · {SITE['address_ko']} · {SITE['opened']} 개관", body)

def page_exhibitions():
    rows=''
    for e in EXH:
        y=e['start'][:4]
        rows+=(f'<a href="/exhibitions/{e["slug"]}/" class="arc-row">'
               f'<div class="top"><span class="yr">{y}</span><span class="ty">{TYPE.get(e["type"],"")}</span></div>'
               f'<div class="ti">{e["title_ko"]}</div><div class="ar">{e.get("subtitle_ko") or ""}</div></a>')
    body=f'''<section class="block wide">
  <h1 class="pg">전시 &nbsp;EXHIBITIONS</h1>
  <div class="arc">{rows}</div>
  <p class="note">2021년 8월 개관 이후의 전시를 동일한 형식으로 보관합니다. 지난 전시도 현재 전시와 같은 구성으로 유지되며, 축소되거나 삭제되지 않습니다.</p>
</section>'''
    write('exhibitions','전시 — 테오화랑','테오화랑 전시 아카이브', body, 'exhibitions')

def page_exhibition(e, prev, nxt):
    h=e.get('hero') or {}
    if h.get('mode')=='poster':
        hero=f'<div class="hero poster">{img(h["src"],"1838/2600","center",e["title_ko"],lazy=False,sizes="(min-width:700px) 400px, 340px")}</div>'
    elif h.get('src'):
        hero=f'<div class="hero">{img(h["src"],None,h.get("pos","center 62%"),e["title_ko"],lazy=False)}</div>'
    else:
        hero=''
    ended = bool(e.get('end'))
    meta=f'''<div class="hero-meta wide">
    <div class="status past">{'Past Exhibition' if ended else 'Exhibition'}</div>
    <h1 class="exh">{e['title_ko']}</h1>
    <div class="who">{e.get('subtitle_ko') or ''}<br>{period(e)}{' · 종료' if ended else ''}</div></div>'''
    body=hero+meta
    if e.get('stub'):
        who=' · '.join(e.get('participants') or []) or (e.get('subtitle_ko') or '')
        links=''.join(f'<a href="/artists/{s}/" class="more">{BYSLUG[s]["name_ko"]}</a>'
                      for s in (e.get('artists') or []) if s in BYSLUG)
        body+=(f'<section class="block mid"><div class="prep-box">'
               f'<p>이 전시의 기록을 정리하고 있습니다.</p>'
               + (f'<p class="w">참여 작가 &nbsp;{who}</p>' if who else '')
               + (f'<div class="btn2">{links}</div>' if links else '')
               + '</div></section>')
    if e.get('lead_ko'):
        body+=f'<section class="block mid"><p class="lead">{e["lead_ko"]}</p></section>'
    if e.get('works'):
        body+=f'<section class="block wide" style="padding-top:0"><span class="eyebrow">Works</span>{works_grid(e["works"])}</section>'
    if e.get('installs'):
        ivs=''.join(img(s,'3/2','center','설치 전경',cls='bcd'[i%3],sizes='(min-width:700px) 50vw, 100vw') for i,s in enumerate(e['installs']))
        body+=f'<section class="block tight wide"><span class="eyebrow">Installation Views</span><div class="installs">{ivs}</div><p class="note">사진 ⓒ {e["credits"].get("사진","—")}</p></section>'
    # 작가 (서문이 없을 때 이 자리가 증거를 대신함)
    linked=[BYSLUG[s] for s in e.get('artists',[]) if s in BYSLUG]
    for a in linked:
        cv=a['cv'].get('주요 이력',[])
        lis=''.join(f'<li><span>{y}</span>{t}</li>' for y,t in cv)
        col=''.join(f'<li><span>—</span>{c}</li>' for c in a['collections'])
        pub=''.join(f'<li><span>—</span>{c}</li>' for c in a['public_works'][:4])
        body+=f'''<section class="block tight mid"><span class="eyebrow">작가</span>
  <div class="two"><div>
    <h3 class="a-nm">{a['name_ko']}</h3><div class="a-en">{a['name_en']}</div>
    <div class="cv-block"><h4>주요 이력</h4><ul>{lis}</ul></div>
    <a href="/artists/{a['slug']}/" class="more">작가 페이지</a></div>
  <div><div class="cv-block"><h4>미술관 소장</h4><ul>{col}</ul></div>
       <div class="cv-block"><h4>공공 설치</h4><ul>{pub}</ul></div></div></div>
  {'<p class="note">이 전시에는 서문이 없었습니다. 화랑이 설명하는 대신 이력과 소장처를 놓아둡니다.</p>' if not e.get('statement_ko') else ''}
</section>'''
    if e.get('statement_ko'):
        ps=''.join(f'<p>{t}</p>' for t in e['statement_ko'])
        by=f'<div class="by">글 · {e["statement_author"]}</div>' if e.get('statement_author') else ''
        body+=f'<section class="block narrow stmt"><span class="eyebrow" style="border-top:none;padding-top:0">서문</span>{ps}{by}</section>'
    rows=[('기간',period(e)),('장소',f"테오화랑<br>{SITE['address_ko']}")]
    if e.get('participants'): rows.append(('참여작가',' · '.join(e['participants'])))
    if linked: rows.append(('참여작가',' · '.join(a['name_ko'] for a in linked)))
    for k,v in (e.get('credits') or {}).items(): rows.append((k,v))
    if not e.get('stub'):
        body+=f'''<section class="block tight mid"><span class="eyebrow">전시 정보</span>{tbl(rows)}
  <p class="note">참여 작가·기획·디자인·사진·후원을 빠짐없이 적습니다. 격은 규모가 아니라 완결성에서 나옵니다.</p></section>'''
    def exlink(x, side):
        if not x: return '<span></span>'
        lab='이전 전시' if side=='prev' else '다음 전시'
        ar='←' if side=='prev' else '→'
        cls='exl'+(' r' if side=='next' else '')
        t=f'<span class="l">{ar} {lab}</span><span class="t">{x["title_ko"]}</span><span class="d">{x["start"][:4]}</span>'
        return f'<a href="/exhibitions/{x["slug"]}/" class="{cls}">{t}</a>'
    body+=('<section class="block tight wide"><div class="exnav">'
           + exlink(prev,'prev') + exlink(nxt,'next') + '</div></section>')
    write(f'exhibitions/{e["slug"]}', f'{e["title_ko"]} — 테오화랑',
          (e.get('lead_ko') or e.get('subtitle_ko') or '')[:120], body, 'exhibitions')

def page_artists():
    body=f'''<section class="block wide">
  <h1 class="pg">작가 &nbsp;ARTISTS</h1>
  <div class="art-grid">{''.join(art_card(a) for a in ART)}</div>
  <p class="note">매체나 장르로 나누지 않습니다. 분류가 밀어낸 작업을 동시대 미술의 한복판으로 데려오는 것이 화랑이 하는 일이므로, 사이트가 다시 분류하지 않습니다.</p>
</section>'''
    write('artists','작가 — 테오화랑','테오화랑과 함께하는 작가들', body, 'artists')

def page_artist(a):
    mine=[e for e in EXH if a['slug'] in (e.get('artists') or [])]
    thin = not (a['lead_ko'] or a['works'] or a['cv'])
    if a.get('portrait'):
        pic=img(a.get('portrait_large') or a.get('portrait'),'4/3',a.get('portrait_pos','center 22%'),
                a['name_ko'],lazy=False,sizes='(min-width:700px) 360px, 100vw')
        credit=f'<p class="note" style="margin-top:20px">사진 ⓒ {a["photo_credit"]}</p>'
    else:
        pic=''; credit=''
    lead = '<p class="lead">'+a['lead_ko']+'</p>' if a['lead_ko'] else ''
    if thin:
        prep = ('<p class="prep-note">이 작가의 프로필을 준비하고 있습니다.'
                + (' 아래 전시에서 작업을 보실 수 있습니다.' if mine else '')+'</p>')
    else:
        prep = ''
    head_=f'''<section class="block wide" style="padding-top:34px"><div class="art-head{'' if pic else ' nopic'}">
  {pic}
  <div><h1 class="exh" style="margin-bottom:6px">{a['name_ko']}</h1>
    <div class="a-en2">{a['name_en']}</div>
    {lead}{prep}{credit}</div>
</div></section>'''
    body=head_
    if a['works']:
        body+=f'<section class="block wide" style="padding-top:0"><span class="eyebrow">Works</span>{works_grid(a["works"])}</section>'
    if mine:
        rows=''.join(f'<div class="r"><span>{e["start"][:4]}</span><span>《{e["title_ko"]}》</span>'
                     f'<span>{TYPE.get(e["type"],"")}</span></div>' for e in mine)
        body+=f'''<section class="block tight mid"><span class="eyebrow">테오화랑과 함께한 전시</span>
  <div class="together">{rows}</div>
  <p class="note">전시 데이터에서 자동 생성됩니다. 이 섹션이 지속 관계의 유일한 물증입니다.</p></section>'''
    if a['collections'] or a['public_works']:
        col=''.join(f'<li><span>—</span>{c}</li>' for c in a['collections'])
        pub=''.join(f'<li><span>—</span>{c}</li>' for c in a['public_works'])
        body+=f'''<section class="block tight mid"><span class="eyebrow">소장 · 설치</span><div class="two">
  <div class="cv-block"><h4>미술관 소장</h4><ul>{col}</ul></div>
  <div class="cv-block"><h4>공공 설치</h4><ul>{pub}</ul></div></div>
  <p class="note">미술관 소장과 공공 설치는 성격이 달라 나누어 표기했습니다.</p></section>'''
    if a['cv']:
        blocks=''
        for k,v in a['cv'].items():
            if k=='주요 이력': continue
            lis=''.join(f'<li><span>{y}</span>{t}</li>' for y,t in v)
            blocks+=f'<div class="cv-block"><h4>{k}</h4><ul>{lis}</ul></div>'
        body+=f'<section class="block tight mid"><span class="eyebrow">CV</span><div class="two">{blocks}</div></section>'
    write(f'artists/{a["slug"]}', f'{a["name_ko"]} — 테오화랑',
          (a['lead_ko'] or f"{a['name_ko']} {a['name_en']}")[:120], body, 'artists')

def page_about():
    CL='<p class="first">'
    ps='<hr class="sep">'.join((CL if i==0 else '<p>')+t+'</p>' for i,t in enumerate(ABOUT['paras']))
    ppl=''.join(f'<div>{img(None,"3/4",ph="인물")}<div class="nm">{p["name"]}</div>'
                f'<div class="ti">{p["title"]}</div></div>' for p in ABOUT['people'])
    body=f'''<section class="block wide">
  <h1 class="pg">화랑 소개 &nbsp;ABOUT</h1>
  <div class="about-text">{ps}</div>
</section>
<section class="block tight wide"><span class="eyebrow">공간</span>
  <div class="two">{img(None,'4/3',ph='공간 사진')}{img(None,'4/3',ph='공간 사진')}</div></section>
<section class="block tight wide"><span class="eyebrow">사람</span>
  <div class="people">{ppl}</div>
  <p class="note">이름과 얼굴이 걸려 있는 것과 없는 것의 신뢰 차이가 이 사이트에서 가장 큰 단일 변수입니다.</p></section>'''
    write('about','화랑 소개 — 테오화랑', ABOUT['paras'][0][:120], body, 'about')

def page_visit():
    rows=[('주소',SITE['address_ko']),('시간',SITE['hours']),('휴관',SITE['closed']),
          ('관람료',SITE['admission']),('지하철',SITE['subway']),('버스',SITE['bus']),
          ('주차',SITE['parking']),('전화',SITE['tel'])]
    body=f'''<section class="block wide">
  <h1 class="pg">오시는 길 &nbsp;VISIT</h1>
  <div class="two"><div>
    {tbl(rows)}
    {tbl([('접근',SITE['access_stairs']),('휠체어',SITE['access_wheelchair'])])}
    <a href="/guide/" class="g-cta"><i>→</i><b>가이드 테오</b>
      <span>화장실 · 주차 · 커피 · 식사 · 한잔<br>화랑 주변에서 필요한 것들, 그리고 좋아하는 곳들</span></a>
    <p class="note">관람료는 무료여도 명시합니다. 상업화랑 문턱을 높게 느끼는 사람이 많습니다.</p></div>
  <div>{img(None,'1/1',ph='지도')}<div style="height:6px"></div>{img(None,'4/3',ph='약도')}</div></div>
</section>'''
    write('visit','오시는 길 — 테오화랑', SITE['address_ko'], body, 'visit')

def page_guide():
    half=[[],[]]
    for i,g in enumerate(GUIDE['groups']): half[0 if i<3 else 1].append(g)
    cols=''
    for side in half:
        col=''
        for g in side:
            items=''
            for it in g['items']:
                tag=f' <em>{it["tag"]}</em>' if it.get('tag') else ''
                items+=f'''<div class="g-item"><div class="nm">{it['name']}</div><div class="walk">{it['walk']}</div>
        <div class="ds">{it['desc']}{tag}</div>
        <div class="g-more"><div class="ad"><b>주소</b>{it['addr']}</div>
          <a href="#" class="mapbtn">네이버 지도</a><a href="#" class="mapbtn">카카오맵</a></div></div>'''
            note=f'<p class="g-note">{g["note"]}</p>' if g.get('note') else ''
            col+=f'<span class="eyebrow">{g["title"]}</span>{note}<div class="g-list">{items}</div>'
        cols+=f'<div>{col}</div>'
    body=f'''<section class="block wide">
  <h1 class="pg">가이드 테오 &nbsp;GUIDE</h1>
  <div class="g-intro">화랑에서 걸어갈 수 있는 곳만 골랐습니다. 많이 담지 않았습니다 &mdash; 테오화랑 사람들이 실제로 가는 곳입니다.</div>
  <div class="two" style="margin-top:34px">{cols}</div>
  <div class="stamp">최종 확인 {GUIDE['updated']} &nbsp;·&nbsp; <em style="font-style:normal">EN</em> 표시는 영어 응대가 가능한 곳입니다</div>
</section>'''
    write('guide','가이드 테오 — 테오화랑','화랑 주변 안내', body)

def page_contact():
    opts=''.join(f'<div><i class="o{" sel" if i==0 else ""}"></i> {t}</div>'
                 for i,t in enumerate(RENTAL['inquiry_types']))
    steps=''.join(f'<div class="s"><div class="n">{i+1:02d}</div><div class="t"><b>{a}</b>{b}</div></div>'
                  for i,(a,b) in enumerate(RENTAL['steps']))
    body=f'''<section class="block wide">
  <h1 class="pg">대관 및 문의 &nbsp;CONTACT</h1>
  <span class="eyebrow">대관 안내</span>
  <div class="notice" style="margin:0 calc(var(--pad)*-1) 22px"><span>{RENTAL['notice']}</span></div>
  <p class="lead" style="margin-bottom:26px">{RENTAL['lead']}</p>
  <div class="two">
    <div><div class="sub-h">공간 사양</div>{tbl(RENTAL['spec'])}</div>
    <div><div class="sub-h">평면도</div>{img(None,'4/3',ph='공간 평면도')}<div style="height:6px"></div>{img(None,'4/3',ph='공간 사진')}</div>
  </div>
  <div class="block tight" style="padding-left:0;padding-right:0"><div class="two">
    <div><div class="sub-h">대관 조건</div>{tbl(RENTAL['terms'])}</div>
    <div><div class="sub-h">진행 절차</div><div class="steps">{steps}</div></div>
  </div></div>
  <div class="mid" style="padding:0">
    <span class="eyebrow">문의</span>
    <div class="form-mock">
      <div class="row"><label>문의 유형</label><div class="opts">{opts}</div></div>
      <div class="row"><label>성함</label><div class="field">—</div></div>
      <div class="row"><label>연락처</label><div class="field">—</div></div>
      <div class="row"><label>내용</label><div class="field" style="min-height:70px">—</div></div>
      <div class="chk"><i></i><span>테오화랑의 전시 소식을 받아보겠습니다.</span></div>
      <a href="#" class="btn-mock">보내기</a>
      <p class="note">영업일 기준 2일 이내에 회신드립니다.</p>
    </div></div>
</section>'''
    write('contact','대관 및 문의 — 테오화랑','테오화랑 대관 안내 및 문의', body, 'contact')

JARPATH=open(os.path.join(ROOT,'jar_path.txt'),encoding='utf-8').read().strip()

if __name__=='__main__':
    page_home(); page_exhibitions(); page_artists(); page_about()
    page_visit(); page_guide(); page_contact()
    for i,e in enumerate(EXH):
        page_exhibition(e, EXH[i+1] if i+1<len(EXH) else None, EXH[i-1] if i>0 else None)
    for a in ART: page_artist(a)
    n=sum(len(f) for _,_,f in os.walk(OUT) if f)
    print(f'생성 완료 — 페이지 {len(EXH)+len(ART)+7}개')
