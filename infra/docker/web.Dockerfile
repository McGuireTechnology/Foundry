FROM node:20

WORKDIR /workspace

RUN corepack enable

COPY package.json pnpm-workspace.yaml tsconfig.base.json /workspace/
COPY apps/web /workspace/apps/web
COPY packages /workspace/packages

RUN pnpm install

EXPOSE 5173

CMD ["pnpm", "--filter", "@foundry/web", "dev", "--host", "0.0.0.0", "--port", "5173"]
