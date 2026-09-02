#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const htmlPath = join(root, "web", "脳トレメーカー.html");
const html = readFileSync(htmlPath, "utf8");

function sourceBetween(start, end) {
  const from = html.indexOf(start);
  const to = html.indexOf(end, from + start.length);
  if (from < 0 || to < 0) throw new Error(`データ定義を抽出できません: ${start}`);
  return html.slice(from + start.length, to).trim();
}

const puzzleSource = sourceBetween("const ILLUSTRATED_DIFF_PUZZLES =", ";\n\nconst ILLUSTRATED_VARIANTS");
const variantSource = sourceBetween("const ILLUSTRATED_VARIANTS =", ";\n\nILLUSTRATED_DIFF_PUZZLES.forEach");
const context = {};
vm.runInNewContext(`puzzles = ${puzzleSource}; variants = ${variantSource};`, context);

const work = mkdtempSync(join(tmpdir(), "spot-diff-validate-"));
let failed = false;

function convert(args) {
  return execFileSync("convert", args, { encoding: "utf8" }).trim();
}

try {
  for (const puzzle of context.puzzles) {
    const variants = {
      "やさしい": { image: puzzle.edited, diffs: puzzle.diffs },
      ...context.variants[puzzle.id],
    };
    const base = join(root, "web", puzzle.base);
    const [width, height] = convert([base, "-format", "%w %h", "info:"]).split(" ").map(Number);

    for (const [difficulty, variant] of Object.entries(variants)) {
      const edited = join(root, "web", variant.image);
      const editedSize = convert([edited, "-format", "%w %h", "info:"]);
      if (editedSize !== `${width} ${height}`) throw new Error(`${puzzle.id}/${difficulty}: 画像サイズが不一致`);
      if (variant.diffs.length !== 7) throw new Error(`${puzzle.id}/${difficulty}: 差分領域が7個ではありません`);

      const mask = join(work, `${puzzle.id}-${difficulty}-mask.png`);
      const finalImage = join(work, `${puzzle.id}-${difficulty}-final.png`);
      const rectangles = variant.diffs.map((d) => {
        const x1 = Math.floor(d.x * width), y1 = Math.floor(d.y * height);
        const x2 = Math.ceil((d.x + d.w) * width), y2 = Math.ceil((d.y + d.h) * height);
        return `rectangle ${x1},${y1} ${x2},${y2}`;
      }).join(" ");
      convert(["-size", `${width}x${height}`, "xc:black", "-fill", "white", "-draw", rectangles, mask]);
      convert([base, edited, mask, "-composite", finalImage]);

      const outsideMean = Number(convert([
        base, finalImage, "-compose", "difference", "-composite",
        "(", mask, "-negate", ")", "-compose", "multiply", "-composite",
        "-format", "%[fx:mean]", "info:",
      ]));
      let itemFailed = false;
      if (outsideMean !== 0) {
        failed = true;
        itemFailed = true;
        console.error(`NG ${puzzle.id}/${difficulty}: 登録領域外に差分あり (${outsideMean})`);
      }

      variant.diffs.forEach((d, index) => {
        const x = Math.floor(d.x * width), y = Math.floor(d.y * height);
        const w = Math.max(1, Math.ceil(d.w * width)), h = Math.max(1, Math.ceil(d.h * height));
        const regionMean = Number(convert([
          base, finalImage, "-compose", "difference", "-composite",
          "-crop", `${w}x${h}+${x}+${y}`, "+repage", "-format", "%[fx:mean]", "info:",
        ]));
        if (regionMean === 0) {
          failed = true;
          itemFailed = true;
          console.error(`NG ${puzzle.id}/${difficulty}: 差分${index + 1}に実画像の変化なし`);
        }
      });
      if (!itemFailed) console.log(`OK ${puzzle.id}/${difficulty}: 7差分・領域外差分0`);
    }
  }
} finally {
  rmSync(work, { recursive: true, force: true });
}

if (failed) process.exit(1);
