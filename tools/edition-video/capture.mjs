// Full-page capture for edition videos. Runs on the render host.
// node capture.mjs URL OUT.png [maxHeightCssPx]
// Prints JSON {ok, title, blocked, textLen} on stdout.
import { createRequire } from "module";
const require = createRequire(process.env.EV_NODE_MODULES ? process.env.EV_NODE_MODULES + "/" : import.meta.url);
const { chromium } = require("playwright-core");
const [url, out, maxH = "4200"] = process.argv.slice(2);
const UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36";
const BLOCK = /captcha|access denied|just a moment|are you a robot|are you human|request blocked|unusual activity|verify you are human/i;
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || "/usr/bin/chromium", headless: true,
  args: ["--hide-scrollbars", "--mute-audio", "--disable-blink-features=AutomationControlled"] });
let res = { ok: false };
try {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.3334,
    userAgent: UA, locale: "en-US", colorScheme: "light" });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {});
  // trigger lazy images, then back to top
  for (let y = 0; y < 5000; y += 700) { await page.evaluate(v => window.scrollTo(0, v), y); await page.waitForTimeout(150); }
  await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(800);
  // strip overlays: cookie banners, ad-block nags, paywall modals, sticky headers
  await page.evaluate(() => {
    for (const el of document.querySelectorAll("body *")) {
      const s = getComputedStyle(el);
      if ((s.position === "fixed" || s.position === "sticky") ) el.remove();
      else if (parseInt(s.zIndex) > 999 && s.position === "absolute") el.remove();
    }
    for (const el of [document.documentElement, document.body]) {
      el.style.setProperty("overflow", "visible", "important"); el.style.setProperty("filter", "none", "important");
      el.style.setProperty("position", "static", "important");
    }
    for (const el of document.querySelectorAll("[class*=blur],[style*=blur]")) el.style.filter = "none";
  });
  const title = await page.title();
  const text = await page.evaluate(() => document.body.innerText || "");
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1440, height: Math.min(h, +maxH) } });
  res = { ok: true, title, textLen: text.length, blocked: BLOCK.test(title + " " + text.slice(0, 3000)) || text.length < 400 };
} catch (e) { res = { ok: false, error: String(e).slice(0, 300) }; }
await browser.close();
console.log(JSON.stringify(res));
