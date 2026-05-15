# Stage 0, "build-stage", based on Bun, to build and compile the frontend
FROM oven/bun:1 AS build-stage

WORKDIR /app

COPY vue/package.json /app/package.json

RUN bun install

COPY ./vue /app
ARG VITE_API_URL

RUN bun run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

COPY --from=build-stage /app/dist/ /usr/share/nginx/html

COPY ./vue/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./vue/nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
