// _scripts/update_citations.mjs
// ─────────────────────────────────────────────────────────────────────
// Fetches your Google Scholar profile and writes _data/citations.json
//
// Requirements: Node.js (already installed — you ran npx prettier)
// No npm install needed — uses only built-in Node.js modules.
//
// Usage:
//   node _scripts/update_citations.mjs
//
// Then commit:
//   git add _data/citations.json
//   git commit -m "chore: update scholar citations"
//   git push
// ─────────────────────────────────────────────────────────────────────

import https from "https";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const SCHOLAR_ID = "MpKhKEUAAAAJ";
const OUTPUT_PATH = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "_data",
  "citations.json"
);
const CURRENT_YEAR = String(new Date().getFullYear());

// ── Fetch a URL and return the HTML ──────────────────────────────────
function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    const options = {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
          "AppleWebKit/537.36 (KHTML, like Gecko) " +
          "Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        Accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      },
    };

    https
      .get(url, options, (res) => {
        // Follow redirects
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          resolve(fetchUrl(res.headers.location));
          return;
        }
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode} for ${url}`));
          return;
        }
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => resolve(data));
      })
      .on("error", reject);
  });
}

// ── Parse the Scholar profile HTML ───────────────────────────────────
function parseHtml(html) {
  // Summary index table — order: Citations-All, Citations-5yr, h-All, h-5yr, i10-All, i10-5yr
  const indices = [...html.matchAll(/class="gsc_rsb_std"[^>]*>(\d+)<\/td>/g)].map(
    (m) => parseInt(m[1], 10)
  );
  const idx = (i) => indices[i] ?? 0;

  console.log("  Index values found:", indices);

  // Papers
  const papers = [];
  const paperBlocks = [...html.matchAll(/<tr[^>]*class="gsc_a_tr"[^>]*>([\s\S]*?)<\/tr>/g)];
  console.log("  Paper rows found:", paperBlocks.length);

  for (const [, block] of paperBlocks) {
    const titleM = block.match(/class="gsc_a_at"[^>]*>([^<]+)<\/a>/);
    const citesM = block.match(/class="gsc_a_ac[^"]*"[^>]*>\s*(\d+)\s*</);
    const yearM  = block.match(/class="gsc_a_y"[\s\S]*?<span[^>]*>(\d{4})<\/span>/);
    const hrefM  = block.match(/href="([^"]*citation_for_view=[^"]+)"/);

    let scholarId = "";
    if (hrefM) {
      const idM = hrefM[1].match(/citation_for_view=([^&"]+)/);
      if (idM) scholarId = decodeURIComponent(idM[1]);
    }

    papers.push({
      title:      titleM ? titleM[1].trim() : "",
      year:       yearM  ? yearM[1]         : "",
      cites:      citesM ? parseInt(citesM[1], 10) : 0,
      scholar_id: scholarId,
    });
  }
  papers.sort((a, b) => b.cites - a.cites);

  // Citations per year histogram
  const yearLabels = [...html.matchAll(/<span[^>]*class="gsc_g_t"[^>]*>(\d{4})<\/span>/g)].map(
    (m) => m[1]
  );
  let yearValues = [...html.matchAll(/<span[^>]*class="gsc_g_al"[^>]*>(\d+)<\/span>/g)].map(
    (m) => parseInt(m[1], 10)
  );
  // Fallback: read from anchor title attributes
  if (!yearValues.length) {
    yearValues = [...html.matchAll(/<a[^>]*class="gsc_g_a"[^>]*title="(\d+)"/g)].map(
      (m) => parseInt(m[1], 10)
    );
  }

  console.log("  Year labels:", yearLabels);
  console.log("  Year values:", yearValues);

  const cites_per_year = {};
  yearLabels.forEach((yr, i) => {
    if (yearValues[i] !== undefined) cites_per_year[yr] = yearValues[i];
  });
  if (!cites_per_year[CURRENT_YEAR]) cites_per_year[CURRENT_YEAR] = 0;

  // Sort years ascending
  const sorted = Object.fromEntries(
    Object.entries(cites_per_year).sort(([a], [b]) => a.localeCompare(b))
  );

  return {
    scholar_id:    SCHOLAR_ID,
    updated:       new Date().toISOString().split("T")[0],
    total:         idx(0),
    since_2021:    idx(1),
    h_index:       idx(2),
    h_index_5y:    idx(3),
    i10_index:     idx(4),
    i10_index_5y:  idx(5),
    cites_per_year: sorted,
    papers,
  };
}

// ── Main ──────────────────────────────────────────────────────────────
async function main() {
  const url =
    `https://scholar.google.com/citations` +
    `?user=${SCHOLAR_ID}&hl=en&pagesize=100&sortby=citationrank`;

  console.log(`Fetching: ${url}`);

  let html;
  try {
    html = await fetchUrl(url);
  } catch (err) {
    console.error(`Failed to fetch page: ${err.message}`);
    process.exit(1);
  }

  // Check for bot detection
  if (html.includes("sorry") && html.includes("unusual traffic")) {
    console.error("Google returned a bot-detection page.");
    console.error("Try again from a different network (e.g. home WiFi vs office).");
    process.exit(1);
  }

  const title = html.match(/<title>([^<]*)<\/title>/)?.[1] ?? "";
  console.log(`Page title: "${title}"`);

  const data = parseHtml(html);

  if (data.total === 0 && data.h_index === 0) {
    // Save debug file so you can inspect what was returned
    const debugPath = OUTPUT_PATH.replace("citations.json", "scholar_debug.html");
    fs.writeFileSync(debugPath, html, "utf8");
    console.error(`\nParsed zeros — saved debug HTML to: ${debugPath}`);
    console.error("Open that file in a browser to see what Scholar returned.");
    process.exit(1);
  }

  fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(data, null, 2), "utf8");

  console.log(`\n✅ Written to ${OUTPUT_PATH}`);
  console.log(`   total=${data.total}  h=${data.h_index}  i10=${data.i10_index}`);
  console.log(`   years=${Object.keys(data.cites_per_year).join(", ")}`);
  console.log(`   papers=${data.papers.length}`);
  console.log(`\nNow run:`);
  console.log(`   git add _data/citations.json`);
  console.log(`   git commit -m "chore: update scholar citations"`);
  console.log(`   git push`);
}

main();
