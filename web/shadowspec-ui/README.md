# shadowspec-ui

ShadowSpec evidence workbench — Next.js static export, deployable to Vercel or GitHub Pages.

## Live demo

`DEMO_URL_PENDING` <!-- replace with the deployed URL once published -->

## Build (static export)

This app is configured for static export (`output: 'export'` in `next.config.mjs`). No API routes are included.

```bash
# Install dependencies
npm install

# Produce a static export in the out/ directory
npx next build
```

The `out/` directory contains the fully-static HTML/CSS/JS bundle. Upload it to any static host (Vercel, GitHub Pages, Netlify, S3, etc.).

### Deploy to Vercel

Import the repo in the [Vercel dashboard](https://vercel.com/new). Vercel detects Next.js automatically; the static-export config means no serverless functions are needed.

### Deploy to GitHub Pages

Push the `out/` directory to the `gh-pages` branch, or configure a GitHub Actions workflow that runs `npx next build` and publishes `out/`.

## Development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

## Project structure

- `pages/index.tsx` — main entry point
- `components/` — CandidateRail, EvidenceDrawer, ScanAnimation, VerdictPanel
- `styles/` — global CSS
- `public/` — static assets
- `next.config.mjs` — static-export configuration

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Static Export](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
