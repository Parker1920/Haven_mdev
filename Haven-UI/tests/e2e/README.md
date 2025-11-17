Playwright E2E tests

To run Playwright tests locally (if Playwright is installed and configured):

1. Ensure the dev server is running (npm run dev) or the API server is running and serving `Haven-UI/dist` (for production build).
2. Install Playwright and browsers (if not installed already):

```bash
cd Haven-UI
npm install
npx playwright install
npx playwright test tests/e2e/admin_login.spec.mjs
```

The tests rely on `HAVEN_ADMIN_PASSWORD` being set in the environment or in `Haven-UI/.env`.
