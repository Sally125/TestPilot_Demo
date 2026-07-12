import { defineConfig } from '@playwright/test';

export default defineConfig({
  outputDir: '.test-results',
  use: {
    browserName: 'chromium',
    screenshot: 'on',
    video: 'retain-on-failure',
    
  },
});
