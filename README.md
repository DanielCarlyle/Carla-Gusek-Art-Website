# Carla Gusek — accessible static art portfolio

Static HTML5/CSS site with a zero-dependency Python build, Decap CMS, GitHub and Netlify.

## Deploy
1. Upload these project files to a new GitHub repository (not the generated `dist` folder).
2. In Netlify choose **Add new project → Import from Git**, select that repository. Netlify reads `netlify.toml`: build `python3 build.py`, publish `dist`.
3. In `admin/config.yml`, replace `REPLACE_WITH_GITHUB_USERNAME/REPLACE_WITH_REPOSITORY` with your repo path.
4. **Authentication is not automatic:** configure a GitHub OAuth app and a compatible hosted OAuth bridge, and replace `REPLACE_WITH_OAUTH_BRIDGE_DOMAIN` with the bridge host. The GitHub OAuth callback must match the bridge's instructions. Netlify Identity/Git Gateway should not be assumed available on new sites. Alternatively configure a supported external Decap auth provider and adjust the backend settings accordingly.
5. Visit `https://your-site.netlify.app/admin/` and sign in with an authorized GitHub account.
6. Add the live site URL to `content/site.json` through Decap for canonical links.

## Content editing
- **Site settings**: intro, About, Purchase, email, social link, SEO, contact form.
- **Artwork gallery**: add, remove and reorder paintings, set titles, images, alt descriptions, availability, price and dimensions. Every saved change commits to GitHub and triggers a Netlify rebuild.
- Images uploaded via CMS go into `assets/uploads/`.

## Important before launch
- The initial artwork image URLs are **referenced from the old website**, not copied. Replace with owned, optimized local files via the CMS before retiring the old website.
- Artwork descriptions, prices and dimensions were not in the provided home-page source and are intentionally blank. Add meaningful descriptions for accessible image alternatives.
- Check the Formspree endpoint belongs to the artist and test a real submission.
- Confirm image rights, final copy, spelling of artwork titles, custom domain, and social metadata.
- Run Lighthouse and axe on the deployed website; WCAG 2.2 AA conformance needs testing and editorial review, not just semantic code.

## Local build
`python3 build.py` then serve the `dist` folder with `python3 -m http.server 8000 --directory dist`.

No framework, runtime JS, jQuery, or build dependencies are needed for the public site. The Decap editor loads JS only under `/admin/`.
