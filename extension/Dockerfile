FROM node:22-alpine

WORKDIR /workspace

RUN npm install -g pnpm

COPY pnpm-lock.yaml package.json pnpm-workspace.yaml ./
COPY extension/package.json ./extension/package.json
COPY extension/tsconfig.json ./extension/tsconfig.json
COPY extension/wxt.config.ts ./extension/wxt.config.ts
COPY extension/eslint.config.js ./extension/eslint.config.js
COPY extension/vitest.config.ts ./extension/vitest.config.ts
COPY extension/vitest.setup.ts ./extension/vitest.setup.ts
COPY extension/src ./extension/src

RUN pnpm install --frozen-lockfile

WORKDIR /workspace/extension

RUN pnpm build

CMD ["sh", "-c", "cp -r .output /workspace/extension-build"]
