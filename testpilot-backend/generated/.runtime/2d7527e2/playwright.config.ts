import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'E:/hkx_project/TestPilot/testpilot-backend/generated/.runtime/2d7527e2',
  outputDir: '.test-results',
  use: {
    browserName: 'chromium',
    screenshot: 'on',
    video: 'retain-on-failure',
  },
});
