# Testing

Install `requirements-dev.txt`, then run `python -m unittest discover -s tests -v`
from the repository root. Integration tests use temporary SQLite databases and
mock provider requests; they do not send email or charge a phone number.

## Browser checks

1. Create a disposable fixture: `python tests/seed_browser_fixture.py /absolute/path/layout.db`.
2. Point both local services' `DATABASE_URL` at that SQLite file. Set
   `ENVIRONMENT=development`, `API_BASE_URL=http://127.0.0.1:8002` and
   `FRONTEND_URL=http://127.0.0.1:8502`. Do not use production secrets or data.
3. Start Uvicorn on port 8002 from `backend` and Streamlit on 8502 from `frontend`.
4. Install Playwright locally if needed (`npm install --no-save --package-lock=false playwright`
   and `npx playwright install chromium`).
5. Run the browser suite:

```javascript
const { chromium } = require('playwright');
const checkLayouts = require('./tests/browser_layout.cjs');
(async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    console.log(await checkLayouts(page, 'http://127.0.0.1:8502', '/absolute/path/qa-output'));
  } finally {
    await browser.close();
  }
})();
```

The suite signs in only to localhost using the fixture account, checks 23 pages
at 320, 390, 768, 1024 and 1440 pixels, checks map tiles and markers, detects
Streamlit exceptions and out-of-viewport controls, and saves screenshots and JSON.
The fixture includes two bookings on the same trail to catch duplicate map keys.
This is responsive smoke coverage, not certification of every interaction or
provider. Live email delivery and live M-Pesa settlement require separately
authorized accounts and explicit end-to-end verification.

For the full browser suite, install the repository's pnpm dependencies and run
`pnpm exec playwright install chromium`, then `pnpm exec playwright test`.
The Playwright configuration starts its own combined server and isolated database.
It refuses to reuse an existing server on the test port. The suite includes
booking mutations, ownership checks, automated accessibility, delayed responses,
and layout checks; it must never run against a live database.
