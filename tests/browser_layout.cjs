const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");

// Use only the isolated database populated by seed_browser_fixture.py.
module.exports = async function checkLayouts(page, baseUrl, outputDir) {
  const url = new URL(baseUrl);
  assert(["localhost", "127.0.0.1"].includes(url.hostname), "Local test server required");
  await fs.mkdir(outputDir, {recursive: true});
  const idle = () => page.locator('[data-testid="stApp"][data-test-script-state="notRunning"]').waitFor();
  await page.goto(baseUrl + "/Login");
  await page.getByRole("heading", {name: "Kilele account"}).waitFor();
  await idle();
  await page.waitForTimeout(500);
  if (await page.getByLabel("Username", {exact: true}).first().isVisible()) {
    await page.getByLabel("Username", {exact: true}).first().fill("layout_tester");
    await page.getByLabel("Password", {exact: true}).first().fill("Kilele-ui-only-47!");
    await page.getByTestId("stFormSubmitButton").getByRole("button", {name: /Sign in/}).click();
  }
  await page.getByText("Signed in as layout_tester", {exact: false}).waitFor();
  const results = [];
  const routes = ["", "Profile", "Login", "Map_View", "Messages", "Wearables", "Strava",
    "Plan_Hike", "Register_for_Hikes", "Manage_Hikes", "Hiking_Gear", "Analytics", "Integrations",
    "Account_and_Support", "Privacy_and_Terms", "2FA_Setup", "Track_Hike", "Emergency_Contacts", "Goals", "Add_Trail",
    "My_Hikes", "Trail_Details?trail=1", "Operations"];
  for (const route of routes) {
    await page.setViewportSize({width: 1440, height: 1000});
    await page.goto(baseUrl + "/" + route);
    await page.locator('[data-testid="stMain"] h1').waitFor();
    await idle();
    // Browser storage restoration triggers a second Streamlit run.
    await page.waitForTimeout(600);
    await idle();
    assert.equal(await page.getByTestId("stException").count(), 0, route + ": Streamlit exception");
    assert.equal(await page.getByText(/Error loading hikes|Hikes could not be loaded/).count(), 0, route + ": data loading failure");
    if (route === "Profile") await page.getByText("Account Information", {exact: true}).waitFor();
    if (route === "Integrations") await page.getByTestId("stDataFrame").waitFor();
    if (route === "Map_View") {
      const frame = page.frameLocator('iframe[title="streamlit_folium.st_folium"]');
      await frame.locator(".leaflet-container").waitFor();
      await frame.locator(".leaflet-tile-loaded").first().waitFor();
      await frame.locator(".leaflet-marker-pane [role=button]").first().waitFor();
      assert(await frame.locator(".leaflet-marker-pane [role=button]").count() > 0, "Map markers missing");
    }
    for (const width of [1440, 1024, 768, 390, 320]) {
      await page.setViewportSize({width, height: 1000});
      await page.waitForTimeout(400);
      const result = await page.evaluate(() => {
        const elements = document.querySelectorAll('[data-testid="stMain"] :is(h1,h2,h3,button,[data-testid="stColumn"],iframe)');
        const overflow = [...elements].filter(el => {
          const r = el.getBoundingClientRect();
          // Scrollable tabs and tables may contain offscreen content intentionally.
          return r.width > 0 && !el.closest('[role="tablist"],[data-testid="stDataFrame"]') &&
            (r.left < -1 || r.right > innerWidth + 1);
        }).map(el => el.tagName + ": " + (el.innerText || el.title || "").slice(0, 80));
        return {width: innerWidth, scrollWidth: document.documentElement.scrollWidth, overflow};
      });
      result.route = route || "Home";
      results.push(result);
      assert(result.scrollWidth <= width, result.route + ": horizontal page overflow");
      assert.deepEqual(result.overflow, [], result.route + ": controls outside viewport");
      assert.equal(await page.getByTestId("stException").count(), 0, route + ": Streamlit exception");
      if ([1440, 390].includes(width)) {
        await page.screenshot({path: path.join(outputDir, result.route.replace(/[^a-zA-Z0-9_-]/g, "_") + "-" + width + ".png")});
      }
    }
  }
  await fs.writeFile(path.join(outputDir, "layout-results.json"), JSON.stringify(results, null, 2));
  return {pages: routes.length, viewportChecks: results.length};
};
