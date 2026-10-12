const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' });
  const page = await browser.newPage({ viewport: { width: 1600, height: 860 }, deviceScaleFactor: 1.5 });
  await page.goto('file:///C:/Users/Admin/.codex/visualizations/2026/08/13/019ffa8f-76f5-70e0-aba2-1ca3cdcd06e7/pytutor-main-function-wireframe.html');
  await page.screenshot({ path: 'C:/Users/Admin/Downloads/Sales-support-AI-pilot/pytutor-main-wireframe.png', fullPage: true });
  await browser.close();
})();
