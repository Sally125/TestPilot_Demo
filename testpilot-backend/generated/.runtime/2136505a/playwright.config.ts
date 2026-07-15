import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'E:/hkx_project/TestPilot/testpilot-backend/generated/.runtime/2136505a',
  outputDir: '.test-results',
  use: {
    browserName: 'chromium',
    screenshot: 'on',
    video: 'retain-on-failure',
  },
});
