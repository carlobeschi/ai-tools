// Scenario tests for assess.html: a simulated developer answers the questionnaire in a real browser,
// then we check the score, label, markers and tags against values worked out by hand from the
// 2026-11-07 snapshot (score per pick = sqrt(devs / leader devs), outside top 10 = 0).
//
// Run from the repo root:   node tests/assess.test.js
// Needs Playwright with Chromium. If the d3 CDN is unreachable, set D3_PATH to a local d3.min.js (v7).
const http = require("http"), fs = require("fs"), path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const TYPES = { ".html": "text/html", ".json": "application/json", ".js": "text/javascript" };
const sqrt = Math.sqrt;

// Expected scores are written out from the snapshot numbers, not computed by the page's own code.
const SCENARIOS = [
  {
    name: "Category leader everywhere",
    picks: { terminal: ["Claude Code"], editors: ["Cursor"], orchestration: ["tmux + git worktrees"], review: ["Claude Code review"],
      context: ["AGENTS.md"], browser: ["Playwright MCP"], sandbox: ["bubblewrap"], local: ["Ollama"], gateways: ["OpenRouter"],
      frameworks: ["LangChain"], evals: ["Arize Phoenix"], assistants: ["OpenClaw"] },
    score: 100, label: "Right with the crowd", markers: 12,
  },
  {
    name: "Strong runners-up",
    picks: { terminal: ["Codex CLI"], editors: ["VS Code + Copilot"] },
    // (sqrt(277/463) + sqrt(130/244)) / 2 = (0.7735 + 0.7299) / 2
    score: Math.round((sqrt(277/463) + sqrt(130/244)) / 2 * 100), label: "Mainstream", markers: 2,
  },
  {
    name: "Mixed stack, one 'none', one custom tool",
    picks: { terminal: ["Claude Code", "Pi"], editors: ["Zed"], orchestration: ["tmux + git worktrees"], review: ["NONE"],
      browser: ["+Puppeteer"], local: ["Ollama"], gateways: ["OpenRouter"], assistants: ["NanoClaw"] },
    // review "none" is left out: 7 categories
    score: Math.round(((1 + sqrt(67/463)) / 2 + sqrt(70/244) + 1 + 1 + 1 + sqrt(3/72) + 0) / 7 * 100), label: "Mainstream", markers: 7,
    offMap: ["Puppeteer"],
  },
  {
    name: "Only invented tools",
    picks: { terminal: ["+MyOwnHarness"], editors: ["+ed(1)"], local: ["+GPU in the basement"] },
    score: 0, label: "Deep niche", markers: 0, offMap: ["MyOwnHarness", "ed(1)", "GPU in the basement"],
  },
  {
    name: "Free text that matches a known tool, in other case",
    picks: { terminal: ["+claude code", "+FooBar"] },
    // "claude code" must resolve to Claude Code (1.0), FooBar is off the map (0) -> mean 0.5
    score: 50, label: "Balanced", markers: 1, offMap: ["FooBar"],
  },
  {
    name: "Scored but niche: outside top 10, and top 10 with 0 devs",
    picks: { terminal: ["Amp"], review: ["Codex Security"] },
    score: 0, label: "Deep niche", markers: 0, offMap: ["Amp"], zeroDevs: ["Codex Security"],
  },
];

function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split(/[?#]/)[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { rsp.writeHead(404); return rsp.end() }
      rsp.writeHead(200, { "content-type": TYPES[path.extname(p)] || "application/octet-stream" }); fs.createReadStream(p).pipe(rsp);
    }).listen(0, () => res(srv));
  });
}

async function newPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  if (process.env.D3_PATH) await page.route("**/d3.min.js", r => r.fulfill({ path: process.env.D3_PATH }));
  await page.route("**fonts.g*/**", r => r.abort());
  const errors = []; page.on("pageerror", e => errors.push(e.message));
  return { page, errors };
}

async function answer(page, picks) {
  for (const [cat, tools] of Object.entries(picks)) {
    const card = `#qgrid .card[data-id="${cat}"]`;
    for (const t of tools) {
      if (t === "NONE") { await page.click(`${card} [data-none]`); continue }
      if (t.startsWith("+")) {           // typed in "Something else"
        if ((await page.getAttribute(`${card} [data-moreb]`, "aria-expanded")) !== "true") await page.click(`${card} [data-moreb]`);
        await page.fill(`${card} input`, t.slice(1)); await page.press(`${card} input`, "Enter"); continue;
      }
      const chip = page.locator(`${card} [data-tool="${t}"]`);
      if (!(await chip.isVisible())) await page.click(`${card} [data-moreb]`);   // tools from "also scored"
      await chip.click();
    }
  }
}

async function readResult(page) {
  return page.evaluate(() => ({
    score: Number(document.getElementById("score").textContent),
    label: document.getElementById("label").textContent,
    markers: document.querySelectorAll("#rgrid .pin").length,
    mine: document.querySelectorAll("#rgrid .tile.mine").length,
    off: [...document.querySelectorAll("#rgrid .tag.out")].map(t => t.textContent.trim()),
    pinLeft: document.querySelector(".me-pin").style.left,
    hash: location.hash,
  }));
}

(async () => {
  const srv = await serve(), base = `http://localhost:${srv.address().port}/assess.html?snapshot=2026-11-07`;
  const browser = await chromium.launch();
  let failed = 0;
  const check = (name, cond, msg) => { if (!cond) { failed++; console.log(`  ✗ ${msg}`) } };

  for (const s of SCENARIOS) {
    const { page, errors } = await newPage(browser);
    await page.goto(base); await page.waitForSelector("#qgrid .chip");
    await answer(page, s.picks);
    await page.click("#go"); await page.waitForTimeout(800);
    const r = await readResult(page);
    const before = failed;
    check(s.name, r.score === s.score, `score ${r.score}, expected ${s.score}`);
    check(s.name, r.label === s.label, `label "${r.label}", expected "${s.label}"`);
    check(s.name, r.markers === s.markers && r.mine === s.markers, `${r.markers} markers / ${r.mine} highlighted tiles, expected ${s.markers}`);
    check(s.name, r.pinLeft === s.score + "%", `person on the bar at ${r.pinLeft}, expected ${s.score}%`);
    for (const n of s.offMap || []) check(s.name, r.off.some(t => t.startsWith(n) && t.endsWith("off the map")), `"${n}" not shown as off the map (${r.off.join(", ")})`);
    for (const n of s.zeroDevs || []) check(s.name, r.off.some(t => t.startsWith(n) && t.endsWith("0 devs")), `"${n}" not shown as 0 devs`);
    check(s.name, !errors.length, `page errors: ${errors.join("; ")}`);

    // the shared link must reproduce the same result in a fresh browser
    const { page: p2 } = await newPage(browser);
    await p2.goto(base + r.hash); await p2.waitForSelector("#result:not([hidden])"); await p2.waitForTimeout(300);
    const r2 = await readResult(p2);
    check(s.name, r2.score === r.score && r2.markers === r.markers, `shared link gives ${r2.score} / ${r2.markers} markers`);
    console.log(`${failed === before ? "✓" : "✗"} ${s.name}: ${r.score} ${r.label}`);
    await page.close(); await p2.close();
  }

  // Edge case: a developer who uses nothing at all
  {
    const { page } = await newPage(browser);
    await page.goto(base); await page.waitForSelector("#qgrid .chip");
    const before = failed;
    check("Uses nothing", await page.isDisabled("#go"), "button enabled with no answers");
    for (const id of await page.$$eval("#qgrid .card", cs => cs.map(c => c.dataset.id))) await page.click(`#qgrid .card[data-id="${id}"] [data-none]`);
    check("Uses nothing", (await page.textContent("#cnt")).includes("12 of 12"), "counter not at 12 of 12");
    check("Uses nothing", await page.isDisabled("#go"), "button enabled when every answer is 'none'");
    // a link holding only "none" answers opens the questionnaire, not an empty result
    const { page: p2 } = await newPage(browser);
    await p2.goto(base + "#terminal=__none__&editors=__none__"); await p2.waitForSelector("#qgrid .chip"); await p2.waitForTimeout(300);
    check("Uses nothing", await p2.isHidden("#result"), "result shown for a 'none only' link");
    console.log(`${failed === before ? "✓" : "✗"} Uses nothing: no score, button stays disabled`);
    await page.close(); await p2.close();
  }

  await browser.close(); srv.close();
  console.log(failed ? `\n${failed} check(s) failed` : "\nAll scenarios pass");
  process.exit(failed ? 1 : 0);
})();
