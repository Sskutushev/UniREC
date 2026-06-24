import { defineConfig } from 'wxt';

export default defineConfig({
  extensionApi: 'chrome',
  srcDir: 'src',
  manifest: {
    name: 'AI Brief Decoder Lite',
    permissions: ['storage'],
    host_permissions: ['http://localhost:8000/*'],
  },
});
