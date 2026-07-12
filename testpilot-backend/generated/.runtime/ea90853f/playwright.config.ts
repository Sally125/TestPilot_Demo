import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    browserName: 'chromium',
    screenshot: 'on',
    video: 'retain-on-failure',
    
  },
});
