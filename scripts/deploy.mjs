#!/usr/bin/env node
// Publish the site without GitHub Actions: sync _site/ to the gh-pages
// branch, which Pages serves directly. Run via `npm run deploy`
// (which builds first). Exits 0 with no push when already current.
import { execFileSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SITE = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(SITE, "_site");
const BRANCH = "gh-pages";

const git = (args, cwd) => execFileSync("git", args, { cwd, stdio: "pipe" }).toString().trim();

const head = git(["rev-parse", "--short", "HEAD"], SITE);
const origin = git(["remote", "get-url", "origin"], SITE);
const work = mkdtempSync(join(tmpdir(), "evw-deploy-"));
try {
  try {
    execFileSync("git", ["clone", "-q", "-b", BRANCH, "--depth", "1", origin, work], { stdio: "pipe" });
  } catch {
    execFileSync("git", ["clone", "-q", "--depth", "1", origin, work], { stdio: "pipe" });
    execFileSync("git", ["checkout", "-q", "--orphan", BRANCH], { cwd: work, stdio: "pipe" });
  }
  execFileSync("git", ["rm", "-rq", "."], { cwd: work, stdio: "pipe" });
  execFileSync("cp", ["-r", `${OUT}/.`, `${work}/`], { stdio: "pipe" });
  execFileSync("touch", [join(work, ".nojekyll")], { stdio: "pipe" });
  execFileSync("git", ["add", "-A"], { cwd: work, stdio: "pipe" });
  if (git(["status", "--porcelain"], work) === "") {
    console.log(`gh-pages is already current with main ${head}; nothing to push.`);
    process.exit(0);
  }
  execFileSync("git", ["commit", "-q", "-m", `Deploy site from main ${head} (local build, no Actions)`],
    { cwd: work, stdio: "pipe" });
  execFileSync("git", ["push", "-q", "origin", BRANCH], { cwd: work, stdio: "inherit" });
  console.log(`Deployed main ${head} to ${BRANCH}.`);
} finally {
  rmSync(work, { recursive: true, force: true });
}
