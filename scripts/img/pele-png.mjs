// Render a Mermaid file to a dark-theme PNG (2400px wide = 1200 CSS px @2x) with pele.
// Runs on iphedeiah: node pele-png.mjs in.mmd out.png
// Needs ~/Projects/pele (npm ci && npm run build) and ~/Projects/ferroprint (npm ci, for playwright-core).
import fs from "node:fs";
import os from "node:os";
const P = process.env.PROJECTS || `${os.homedir()}/Projects`;
const { render } = await import(`${P}/pele/dist/pele.js`);
const { chromium } = await import(`${P}/ferroprint/node_modules/playwright-core/index.mjs`);
const [, , src, out] = process.argv;
const { svg } = render(fs.readFileSync(src, "utf8"));
const html = `<!doctype html><style>html,body{margin:0;background:#15202b}
.wrap{width:1200px;padding:40px;box-sizing:border-box}
.pele{--pele-bg:#15202b;--pele-fg:#e7e9ea;--pele-muted:#8b98a5;--pele-line:#8b98a5;--pele-surface:#1e2732;
--pele-surface-alt:#273340;--pele-border:#38444d;--pele-accent:#1d9bf0;--pele-font:system-ui,sans-serif}
svg{width:100%;height:auto}</style><div class="wrap">${svg}</div>`;
const b = await chromium.launch({ executablePath: process.env.CHROME || "/usr/bin/chromium" });
const p = await b.newPage({ viewport: { width: 1200, height: 400 }, deviceScaleFactor: 2 });
await p.setContent(html);
await p.locator(".wrap").screenshot({ path: out });
await b.close();
console.log(out);
