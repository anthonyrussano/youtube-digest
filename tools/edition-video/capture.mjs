// Full-page and X-post capture for edition videos. Runs on the render host.
//   node capture.mjs URL OUT.png [maxHeightCssPx]
//   node capture.mjs --xpost ID OUT.png
// Prints JSON {ok, title, blocked, textLen, mode, light, mean, headline} on stdout.
// Dark mode is on by default (colorScheme + Chromium force-dark). Set EV_DARK=0 to
// turn it off. If a page stays light, build.py inverts the PNG and keeps photos,
// or frames the article on a dark card.
import { createRequire } from "module";
const require = createRequire(process.env.EV_NODE_MODULES ? process.env.EV_NODE_MODULES + "/" : import.meta.url);
const { chromium } = require("playwright-core");

const DARK = process.env.EV_DARK !== "0" && process.env.EV_DARK !== "false";
const UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36";
const BLOCK = /captcha|access denied|just a moment|are you a robot|are you human|request blocked|unusual activity|verify you are human/i;
const XFAIL = /log in to x|sign in to x|something went wrong|this post (is )?unavailable|doesn’t exist|doesn't exist|has been deleted|try again|this content is not available/i;

const args = ["--hide-scrollbars", "--mute-audio", "--disable-blink-features=AutomationControlled"];
if (DARK) {
  args.push("--enable-features=WebContentsForceDark", "--force-dark-mode",
            "--blink-settings=forceDarkModeEnabled=true");
}

function flag(name) {
  const i = process.argv.indexOf(name);
  return i >= 0 ? { i, val: process.argv[i + 1] } : null;
}

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM || "/usr/bin/chromium",
  headless: true,
  args,
});
let res = { ok: false, dark: DARK };
try {
  const xp = flag("--xpost");
  if (xp) res = await captureXPost(browser, xp.val, process.argv[xp.i + 2]);
  else {
    const [url, out, maxH = "4200"] = process.argv.slice(2);
    res = await capturePage(browser, url, out, maxH);
  }
} catch (e) {
  res = { ok: false, error: String(e).slice(0, 300), dark: DARK };
}
await browser.close();
console.log(JSON.stringify(res));

async function context(browser, viewport, dsf = 1.3334) {
  return browser.newContext({
    viewport,
    deviceScaleFactor: dsf,
    userAgent: UA,
    locale: "en-US",
    colorScheme: DARK ? "dark" : "light",
  });
}

async function dismissChrome(page) {
  await page.evaluate(() => {
    for (const el of document.querySelectorAll("body *")) {
      const s = getComputedStyle(el);
      if (s.position === "fixed" || s.position === "sticky") el.remove();
      else if (parseInt(s.zIndex) > 999 && s.position === "absolute") el.remove();
    }
    for (const el of [document.documentElement, document.body]) {
      el.style.setProperty("overflow", "visible", "important");
      el.style.setProperty("position", "static", "important");
    }
    for (const el of document.querySelectorAll("[class*=blur],[style*=blur]")) el.style.filter = "none";
  });
}

async function headlineBox(page) {
  return page.evaluate(() => {
    const h = document.querySelector("article h1, main h1, [itemprop='headline'], h1");
    if (!h) return { y: 0, text: "" };
    const r = h.getBoundingClientRect();
    const y = Math.max(0, window.scrollY + r.top - 28);
    return { y, text: (h.innerText || "").replace(/\s+/g, " ").trim().slice(0, 200) };
  });
}

async function lumaOfPng(ctx, shot) {
  // Measure on a blank page so any page CSS cannot skew the reading.
  const tmp = await shot;
  const b64 = tmp.toString("base64");
  const p2 = await ctx.newPage();
  try {
    await p2.setContent("<html><body></body></html>");
    return await p2.evaluate(async (b64) => {
      const img = new Image();
      const loaded = new Promise((res, rej) => { img.onload = res; img.onerror = rej; });
      img.src = "data:image/png;base64," + b64;
      await loaded;
      const c = document.createElement("canvas");
      c.width = img.width; c.height = img.height;
      const cx = c.getContext("2d");
      cx.drawImage(img, 0, 0);
      const data = cx.getImageData(0, 0, c.width, c.height).data;
      let sum = 0, n = 0, step = 16 * 4;
      for (let i = 0; i < data.length; i += step) {
        sum += (data[i] + data[i + 1] + data[i + 2]) / 3;
        n++;
      }
      const mean = n ? sum / n : 255;
      return { mean, light: mean > 165 };
    }, b64);
  } finally {
    await p2.close();
  }
}

async function capturePage(browser, url, out, maxH) {
  const ctx = await context(browser, { width: 1440, height: 900 });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {});
  for (let y = 0; y < 5000; y += 700) {
    await page.evaluate(v => window.scrollTo(0, v), y);
    await page.waitForTimeout(150);
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(600);
  await dismissChrome(page);
  await page.waitForTimeout(200);

  const head = await headlineBox(page);
  const total = await page.evaluate(() => document.documentElement.scrollHeight);
  const clipY = Math.max(0, Math.min(head.y, Math.max(0, total - 900)));
  const clipH = Math.max(900, Math.min(total - clipY, +maxH));
  const clip = { x: 0, y: clipY, width: 1440, height: clipH };

  await page.screenshot({ path: out, fullPage: true, clip, type: "png" });
  let mean = null, light = false;
  try {
    const sample = await lumaOfPng(ctx, page.screenshot({
      fullPage: true, clip: { ...clip, height: Math.min(clip.height, 500) }, type: "png",
    }));
    mean = sample.mean;
    light = sample.light;
  } catch {}
  const title = await page.title();
  const text = await page.evaluate(() => document.body.innerText || "");
  await ctx.close();
  return {
    ok: true, title, textLen: text.length, dark: DARK, mode: "page",
    blocked: BLOCK.test(title + " " + text.slice(0, 3000)) || text.length < 400,
    inverted: false, light, mean, headline: head.text, headlineY: clipY,
  };
}

async function captureXPost(browser, id, out) {
  const theme = DARK ? "dark" : "light";
  const embed = `https://platform.twitter.com/embed/Tweet.html?id=${id}&theme=${theme}&dnt=true&hideThread=true`;
  const ctx = await context(browser, { width: 1600, height: 1600 }, 2);
  const page = await ctx.newPage();
  await page.goto(embed, { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(1200);
  for (const frame of page.frames()) {
    try {
      await frame.waitForSelector("article, [data-testid='tweet'], .tweet", { timeout: 4000 });
    } catch {}
  }
  await page.waitForTimeout(800);
  const info = await page.evaluate(() => {
    const text = document.body ? document.body.innerText || "" : "";
    const article = document.querySelector("article, [data-testid='tweet']");
    const iframe = document.querySelector("iframe");
    return { text, hasArticle: !!article, hasIframe: !!iframe, title: document.title };
  });
  let failed = XFAIL.test(info.text) || (info.text.replace(/\s+/g, " ").trim().length < 40 && !info.hasArticle && !info.hasIframe);
  if (!failed) {
    const shot = await screenshotTweet(page);
    if (shot) {
      const fs = await import("fs");
      fs.writeFileSync(out, shot);
      await ctx.close();
      return { ok: true, title: info.title, textLen: info.text.length, dark: DARK, mode: "embed" };
    }
  }
  await ctx.close();
  return { ok: false, error: failed ? "embed did not render" : "no tweet box to crop", title: info.title,
           textLen: info.text.length, dark: DARK, mode: "embed" };
}

async function screenshotTweet(page) {
  const targets = [];
  const handle = await page.$("article, [data-testid='tweet']");
  if (handle) targets.push(handle);
  for (const frame of page.frames()) {
    try {
      const h = await frame.$("article, [data-testid='tweet'], .EmbeddedTweet, #app, body");
      if (h) targets.push(h);
    } catch {}
  }
  for (const el of targets) {
    try {
      const box = await el.boundingBox();
      if (!box || box.width < 200 || box.height < 80) continue;
      const pad = 16;
      const clip = {
        x: Math.max(0, box.x - pad),
        y: Math.max(0, box.y - pad),
        width: Math.min(1600, box.width + pad * 2),
        height: Math.min(1600, box.height + pad * 2),
      };
      return await page.screenshot({ clip, type: "png" });
    } catch {}
  }
  const iframe = await page.$("iframe");
  if (iframe) {
    const box = await iframe.boundingBox();
    if (box && box.width > 200 && box.height > 80) {
      const pad = 16;
      return await page.screenshot({
        clip: {
          x: Math.max(0, box.x - pad),
          y: Math.max(0, box.y - pad),
          width: Math.min(1600, box.width + pad * 2),
          height: Math.min(1600, box.height + pad * 2),
        },
        type: "png",
      });
    }
  }
  return null;
}
