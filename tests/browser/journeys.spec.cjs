const {test, expect} = require("@playwright/test");
const AxeBuilder = require("@axe-core/playwright").default;
const checkLayouts = require("../browser_layout.cjs");
const path = require("node:path");

async function idle(page) {
  await expect(page.locator('[data-testid="stApp"]')).toHaveAttribute("data-test-script-state", "notRunning");
  await expect(page.getByTestId("stException")).toHaveCount(0);
}

async function login(page, username) {
  await page.goto("/Login");
  await expect(page.getByRole("heading", {name: "Kilele account"})).toBeVisible();
  await page.getByLabel("Username", {exact: true}).first().fill(username);
  await page.getByLabel("Password", {exact: true}).first().fill("Kilele-ui-only-47!");
  await page.getByTestId("stFormSubmitButton").getByRole("button", {name: "Sign in", exact: true}).click();
  await expect(page.getByText("Signed in as " + username, {exact: false})).toBeVisible();
  await idle(page);
}

test("mobile visitor can sign in, resume a booking, cancel, and rebook", async ({page}) => {
  await page.setViewportSize({width: 390, height: 844});
  await page.goto("/Trail_Details?trail=1");
  await expect(page.getByRole("heading", {name: "Upcoming group hikes"})).toBeVisible();
  await page.getByRole("link", {name: "Review and book", exact: false}).first().click();
  await expect(page.getByRole("heading", {name: "Confirm your place"})).toBeVisible();
  await page.getByRole("link", {name: "Sign in to book", exact: false}).click();
  await page.getByLabel("Username", {exact: true}).first().fill("journey_member");
  await page.getByLabel("Password", {exact: true}).first().fill("Kilele-ui-only-47!");
  // Submit by keyboard, preserving native form focus and activation.
  await page.getByLabel("Password", {exact: true}).first().press("Enter");
  await expect(page.getByText("Signed in as journey_member", {exact: false})).toBeVisible();
  await page.getByRole("link", {name: "Continue booking", exact: false}).click();
  await page.getByRole("checkbox", {name: "Confirm my place"}).check();
  await page.getByRole("button", {name: "Confirm free booking", exact: false}).click();
  await expect(page.getByText(/Your place is confirmed. Booking reference/)).toBeVisible();
  await expect(page.getByRole("heading", {name: "My hikes", exact: true})).toBeVisible();
  await expect(page.getByText("Confirmed", {exact: true})).toBeVisible();
  await page.reload();
  await expect(page.getByText("Confirmed", {exact: true})).toBeVisible();
  await page.getByText("Cancel my place", {exact: true}).click();
  await page.getByRole("checkbox", {name: "Cancel this booking"}).check();
  await page.getByRole("button", {name: "Cancel booking", exact: false}).click();
  await expect(page.getByText("Registration cancelled. Your place has been released.", {exact: true})).toBeVisible();
  await page.getByRole("tab", {name: "Cancelled", exact: true}).click();
  await expect(page.getByText("Cancelled", {exact: true}).last()).toBeVisible();
  await page.goto("/Register_for_Hikes?event=1");
  await page.getByRole("checkbox", {name: "Confirm my place"}).check();
  await page.getByRole("button", {name: "Confirm free booking", exact: false}).click();
  await expect(page.getByText(/Your place is confirmed. Booking reference/)).toBeVisible();
  await idle(page);
});

test("organizer tools are denied to a member; paid checkout stays disabled", async ({page}) => {
  await login(page, "journey_member");
  await page.goto("/Operations");
  await expect(page.getByText("Administrator access required.", {exact: true})).toBeVisible();
  await page.goto("/Register_for_Hikes?event=2");
  await expect(page.getByText("Paid bookings are currently unavailable. No payment will be collected.", {exact: true})).toBeVisible();
  await expect(page.getByRole("button", {name: "Pay with M-Pesa", exact: false})).toHaveCount(0);
});

test("operations exposes missing email and backup status without crashing", async ({page}) => {
  await login(page, "layout_tester");
  await page.goto("/Operations");
  await expect(page.getByRole("heading", {name: "Encrypted backups", exact: true})).toBeVisible();
  await expect(page.getByText("Email is not authorized. Queued notices cannot be delivered yet.", {exact: true})).toBeVisible();
  await expect(page.getByText("No recorded backup outcome yet. Check GitHub Actions before relying on recovery.", {exact: true})).toBeVisible();
  await idle(page);
});

test("delayed frontend responses still produce a usable sign-in page", async ({page}) => {
  await page.route("**/static/**", async route => {
    await new Promise(resolve => setTimeout(resolve, 350));
    await route.continue();
  });
  await page.goto("/Login");
  await expect(page.getByLabel("Username", {exact: true}).first()).toBeVisible();
  await expect(page.getByRole("button", {name: "Sign in", exact: true})).toBeEnabled();
  await idle(page);
});

test("critical visitor pages meet automated WCAG A and AA checks", async ({page}) => {
  for (const route of ["/Login", "/Register_for_Hikes?event=1", "/Trail_Details?trail=1"]) {
    await page.goto(route);
    await expect(page.locator('[data-testid="stMain"] h1')).toBeVisible();
    await idle(page);
    const results = await new AxeBuilder({page}).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    expect(results.violations.map(v => ({id: v.id, help: v.help, nodes: v.nodes.map(n => n.target)}))).toEqual([]);
  }
});

test("authenticated pages fit mobile, tablet, and desktop widths", async ({page}, testInfo) => {
  test.setTimeout(300000);
  const result = await checkLayouts(page, "http://127.0.0.1:8503", path.join(testInfo.outputDir, "layouts"));
  expect(result.viewportChecks).toBe(115);
});
