import { defineConfig } from '@playwright/test';

export default defineConfig({
  outputDir: '.test-results',
  use: {
    browserName: 'chromium',
    screenshot: 'on',
    video: 'retain-on-failure',
    storageState: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/1/profile-2.json',
  },
});
