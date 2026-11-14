
"""Zero-dependency static build. Run: python3 build.py"""

import json
import html
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
OUT = ROOT / 'dist'

site = json.loads((ROOT / 'content/site.json').read_text(encoding='utf-8'))
items = json.loads((ROOT / 'content/artworks.json').read_text(encoding='utf-8'))['items']

# Rebuild the static output directory
if OUT.exists():
    shutil.rmtree(OUT)

OUT.mkdir()

# Copy site assets and Decap CMS admin files
shutil.copytree(ROOT / 'assets', OUT / 'assets')
shutil.copytree(ROOT / 'admin', OUT / 'admin')

# Ensure Decap CMS uploaded images are included
uploads_source = ROOT / 'assets/uploads'
uploads_destination = OUT / 'assets/uploads'

if uploads_source.exists():
    shutil.copytree(
        uploads_source,
        uploads_destination,
        dirs_exist_ok=True
    )


def esc(x):
    return html.escape(str(x or ''), quote=True)


def path(s):
    s = str(s or '')
    if s.startswith(('https://', 'http://')):
        return s
    return '/' + s.lstrip('/')


def safeurl(s):
    s = path(s)
    return s if s.startswith('/') or urlparse(s).scheme == 'https' else '#'


def page(title, main, desc=None):
    name = esc(site['artist_name'])
    description = esc(desc or site['description'])

    canonical = site.get('site_url', '').rstrip('/')
    canon = (
        f'<link rel="canonical" href="{esc(canonical + title[1])}">'
        if canonical else ''
    )

    social = site.get('social_image', '')
    og = (
        f'<meta property="og:image" content="{esc(safeurl(social))}">'
        if social else ''
    )

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>{esc(title[0])} | {name}</title>
<meta name="description" content="{description}">

<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title[0])} | {name}">
<meta property="og:description" content="{description}">
{og}
{canon}

<meta name="theme-color" content="#ffffff">
<link rel="stylesheet" href="/assets/site.css">
</head>

<body>

<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <div class="container header-inner">

    <!-- Carla Gusek logo -->
    <a class="brand site-logo"
       href="/"
       aria-label="{name}, home">

      <img
        src="/assets/uploads/carla-gusek-website-logo.png"
        alt="{name}"
        width="180"
        height="90"
        decoding="async"
      >

    </a>

    <nav aria-label="Main navigation">
      <ul>
        <li><a href="/">My Work</a></li>
        <li><a href="/about/">About Me</a></li>
        <li><a href="/purchase/">Make a Purchase</a></li>
      </ul>
    </nav>

  </div>
</header>

<main id="main" class="container">
{main}
</main>

<footer class="site-footer">
  <div class="container footer-grid">

    <section aria-labelledby="contact-title">
      <h2 id="contact-title">{esc(site['contact_heading'])}</h2>

      <form action="{esc(safeurl(site['formspree_url']))}" method="POST">

        <label for="email">Your email</label>
        <input
          id="email"
          name="email"
          type="email"
          autocomplete="email"
          required
        >

        <label for="message">Your message</label>
        <textarea
          id="message"
          name="message"
          rows="5"
          required
        ></textarea>

        <button type="submit">Send message</button>

      </form>
    </section>

    <section aria-labelledby="follow-title">
      <h2 id="follow-title">Follow</h2>

      <p>
        <a href="{esc(safeurl(site['instagram_url']))}"
           rel="noopener noreferrer"
           target="_blank">
          Instagram
          <span class="visually-hidden">(opens in new tab)</span>
        </a>
      </p>

      <p>
        <a href="mailto:{esc(site['contact_email'])}">
          Email Carla
        </a>
      </p>
    </section>

  </div>

  <div class="container copyright">
    © {name}. All rights reserved.
  </div>

</footer>

</body>
</html>'''


def write(route, markup):
    dest = OUT / route / 'index.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(markup, encoding='utf-8')


# Generate gallery cards and individual artwork pages
cards = []

for i, a in enumerate(items):
    slug = a['slug']

    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Invalid artwork slug: ' + slug)

    if a.get('featured', True):
        cards.append(
            f'<article class="art-card">'
            f'<a href="/art/{esc(slug)}/">'
            f'<div class="art-image">'
            f'<img src="{esc(safeurl(a["image"]))}" '
            f'alt="{esc(a.get("description") or "Abstract painting titled " + a["title"])}" '
            f'loading="lazy" decoding="async" width="720" height="720">'
            f'</div>'
            f'<h2>{esc(a["title"])}</h2>'
            f'</a>'
            f'</article>'
        )

    details = ''.join(
        f'<p><strong>{label}:</strong> {esc(a[field])}</p>'
        for field, label in [
            ('medium', 'Medium'),
            ('dimensions', 'Dimensions'),
            ('price', 'Price'),
            ('availability', 'Availability')
        ]
        if a.get(field)
    )

    description_html = (
        '<p>' + esc(a["description"]) + '</p>'
        if a.get("description") else ""
    )

    main = (
        f'<p class="back"><a href="/">← All artwork</a></p>'
        f'<article class="detail">'
        f'<div>'
        f'<img src="{esc(safeurl(a["image"]))}" '
        f'alt="{esc(a.get("description") or "Abstract painting titled " + a["title"])}" '
        f'width="1000" height="1000">'
        f'</div>'
        f'<div>'
        f'<h1>{esc(a["title"])}</h1>'
        f'{description_html}'
        f'{details}'
        f'<p><a class="button-link" href="/purchase/">'
        f'Enquire about this artwork'
        f'</a></p>'
        f'</div>'
        f'</article>'
    )

    write(
        'art/' + slug,
        page(
            (a['title'], '/art/' + slug + '/'),
            main,
            a.get('description') or None
        )
    )


# Homepage
write(
    '',
    page(
        ('My Work', '/'),
        f'<section class="intro">'
        f'<h1>{esc(site["artist_name"])}</h1>'
        f'<p>{esc(site["intro"])}</p>'
        f'</section>'
        f'<section aria-label="Artwork gallery" class="gallery">'
        f'{"".join(cards)}'
        f'</section>'
    )
)


# About page
write(
    'about',
    page(
        (site['about_heading'], '/about/'),
        f'<section class="text-page">'
        f'<h1>{esc(site["about_heading"])}</h1>'
        f'<p>{esc(site["about_text"])}</p>'
        f'</section>'
    )
)


# Purchase page
write(
    'purchase',
    page(
        (site['purchase_heading'], '/purchase/'),
        f'<section class="text-page">'
        f'<h1>{esc(site["purchase_heading"])}</h1>'
        f'<p>{esc(site["purchase_text"])}</p>'
        f'<p><a href="mailto:{esc(site["contact_email"])}">'
        f'Email to enquire about artwork'
        f'</a></p>'
        f'</section>'
    )
)


# Search engine crawler instructions
(OUT / 'robots.txt').write_text(
    'User-agent: *\nAllow: /\n',
    encoding='utf-8'
)

print('Built', len(items), 'artwork pages in', OUT)
