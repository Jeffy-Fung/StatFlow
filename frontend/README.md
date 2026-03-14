# StatFlow – Frontend

This is the frontend for the [StatFlow](https://github.com/Jeffy-Fung/StatFlow) project, built with [Next.js](https://nextjs.org), TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework**: [Next.js 16](https://nextjs.org) (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Linting**: ESLint (Next.js config)

## Getting Started

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the app.

## Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start the development server |
| `npm run build` | Create an optimised production build |
| `npm run start` | Serve the production build locally |
| `npm run lint` | Run ESLint |

## Project Structure

```
frontend/
├── src/
│   └── app/
│       ├── layout.tsx   # Root layout (metadata, global styles)
│       ├── page.tsx     # Landing page
│       └── globals.css  # Global CSS / Tailwind entry-point
├── public/              # Static assets
├── next.config.ts
├── tsconfig.json
└── package.json
```
