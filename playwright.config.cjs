const {defineConfig} = require("@playwright/test");
const path = require("node:path");
const database = path.resolve("browser-tests.db").replaceAll("\\", "/");

module.exports = defineConfig({
  testDir: "./tests/browser",
  timeout: 120000,
  expect: {timeout: 30000},
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"], ["html", {open: "never"}]],
  use: {
    baseURL: "http://127.0.0.1:8503",
    browserName: "chromium",
    viewport: {width: 1440, height: 1000},
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "python tests/seed_browser_fixture.py browser-tests.db && python scripts/serve_hosted.py",
    url: "http://127.0.0.1:8503/_ready",
    timeout: 120000,
    reuseExistingServer: false,
    env: {
      DATABASE_URL: "sqlite:///" + database,
      ENVIRONMENT: "development", DEBUG: "false",
      PORT: "8503", STREAMLIT_PORT: "8504",
      FRONTEND_URL: "http://127.0.0.1:8503",
      API_BASE_URL: "http://127.0.0.1:8503", PYTHONUTF8: "1",
    },
  },
});
