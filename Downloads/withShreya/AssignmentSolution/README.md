# Expense Tracker

A full-stack, single-page application (SPA) that helps users monitor, categorize, and visualize their personal spending habits in real time.

---

## Problem Statement

Managing day-to-day expenses is difficult without a centralized tool. This application solves the problem of keeping track of daily financial activity by letting users quickly log purchases, edit or remove past entries, and see live visual summaries of where their money goes — all within a single, seamless interface that never reloads the page.

---

## Technical Stack

| Layer        | Technology |
|--------------|------------|
| Frontend     | React 19 (Vite) |
| Styling      | Tailwind CSS v4 (utility-first, mobile-first) |
| Routing/State | React Hooks (`useState`, `useEffect`, `useCallback`, `useMemo`) — tab-based SPA navigation with no router library needed |
| HTTP Client  | Axios |
| Charts       | Chart.js + react-chartjs-2 |
| Backend      | Node.js + Express 5 |
| Database     | SQLite3 (via `sqlite3` npm package) |
| Dev Tooling  | `concurrently` (run backend + frontend with one command), ESLint, PostCSS, Autoprefixer |
| Deployment   | Local (run with `npm start`); can be deployed to any Node-capable host |

---

## Feature List

- **True SPA Experience** — Tab navigation rewrites the current page in React state; zero full-page reloads.
- **Full CRUD on Database** — Create, Read, Update, and Delete expense records via a RESTful Express API backed by SQLite.
- **Add Expense Form** — Captures title, amount, category, date, and optional description with built-in HTML5 validation.
- **Expense Logbook** — Sortable by Date, Title, or Amount (ascending/descending toggle); real-time search filters by title or category.
- **Inline Edit Flow** — Clicking Edit pre-fills the form and switches to the edit tab; Cancel returns to the logbook without saving.
- **Dashboard Analytics** — Live overview cards (Total Spending, Top Category, Transaction Count) plus a Category Doughnut chart and a Monthly Trend bar chart.
- **Responsive Mobile Design** — Mobile-first Tailwind grid; action buttons always visible on touch screens, hover-hidden only on desktop.
- **Graceful Error Handling** — Full-page fallback UI with a Retry button when the backend is unreachable; toast banner for non-fatal API errors.
- **Modern Aesthetics** — Gradient headers, glassmorphism cards, smooth fade/slide-in animations, and Lucide-react iconography.
- **Performance** — `useMemo` for chart data computation; optimistic local-state updates so the UI feels instant.

---

## Folder Structure

```
AssignmentSolution/
├── backend/
│   ├── server.js          # Express REST API — all CRUD routes + SQLite setup
│   └── package.json       # Backend dependencies (express, sqlite3, cors)
├── database/
│   └── schema.sql         # Portable SQL schema + sample seed data
├── frontend/
│   ├── index.html         # Single HTML entry point (SPA shell)
│   ├── vite.config.js     # Vite config — proxies /api to backend port
│   ├── tailwind.config.js # Tailwind content paths
│   └── src/
│       ├── main.jsx           # React root mount
│       ├── App.jsx            # Top-level layout, tab state, edit orchestration
│       ├── components/
│       │   ├── Dashboard.jsx  # Overview cards + Chart.js visualizations
│       │   ├── ExpenseForm.jsx# Add / Edit form with controlled inputs
│       │   └── ExpenseList.jsx# Searchable, sortable logbook table
│       ├── hooks/
│       │   └── useExpenses.js # Custom hook — all API calls + shared expense state
│       └── services/
│           └── api.js         # Axios wrappers for each CRUD endpoint
├── .gitignore
├── package.json               # Root scripts — `npm start` runs everything together
└── README.md
```

---

## Getting Started

### Prerequisites
- Node.js v18+
- npm v9+

### Installation & Run

```bash
# 1. Install all dependencies (root + backend + frontend)
npm run install:all

# 2. Start both servers concurrently
npm start
```

| Server   | URL                    |
|----------|------------------------|
| Frontend | http://localhost:5173  |
| Backend  | http://localhost:3001  |

The Vite dev server proxies all `/api` requests to the Express backend, so the app behaves as a single origin — no CORS configuration needed during development.

### Database

The SQLite database (`backend/database.sqlite`) is created automatically on first run. To start with a fresh schema and sample data, run:

```bash
# Requires sqlite3 CLI
sqlite3 backend/database.sqlite < database/schema.sql
```

---

## Challenges Overcome

1. **Async React state + API timing** — Updates to the expense list had to feel instant while waiting for SQLite. The solution was a custom `useExpenses` hook that applies optimistic local-state changes immediately and rolls back on API failure, keeping the UI snappy without sacrificing data integrity.

2. **Vite proxy for single-origin development** — Running a React dev server on port 5173 and Express on port 3001 would normally require CORS configuration on every request. Configuring Vite's built-in proxy to forward `/api/*` to `localhost:3001` eliminated this entirely and mirrors how a production reverse-proxy would behave.

3. **Mobile touch accessibility** — The initial design hid Edit/Delete buttons behind a CSS hover state (`opacity-0 group-hover:opacity-100`), which is invisible on touch devices. Fixed with Tailwind's responsive prefix (`sm:opacity-0 sm:group-hover:opacity-100`) so buttons are always visible on small screens and hidden-until-hover on desktop only.

4. **Chart data memoization** — Recomputing category totals and monthly aggregates on every render caused chart flicker. Wrapping both computations in `useMemo` with `[expenses]` as the dependency resolved this cleanly.

5. **Edit-mode state orchestration** — Coordinating the active tab, the pre-filled form, and the cancel/save flow across three sibling components without a global state library required lifting edit state to `App.jsx` and passing targeted callbacks, keeping each component's responsibility clear.
