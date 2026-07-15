import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'E:/hkx_project/TestPilot/testpilot-backend/generated/.runtime/33139687',
  outputDir: '.test-results',
  use: {
    browserName: 'chromium',
    screenshot: 'on',
    video: 'retain-on-failure',
  },
});
