import { chromium } from "playwright";

export async function capture(url: string, output: string) {
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1440, height: 2000 }
  });

  await page.goto(url, { waitUntil: "networkidle" });
  await page.screenshot({
    path: output,
    fullPage: true
  });

  await browser.close();
}
