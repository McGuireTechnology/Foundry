FROM node:20

WORKDIR /workspace

RUN corepack enable

COPY package.json pnpm-workspace.yaml tsconfig.base.json /workspace/
COPY apps/docs /workspace/apps/docs

RUN pnpm install

EXPOSE 5174

CMD ["pnpm", "--filter", "@foundry/docs", "dev", "--host", "0.0.0.0"]
