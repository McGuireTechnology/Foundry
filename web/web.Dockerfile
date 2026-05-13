FROM node:20

WORKDIR /workspace/web

COPY web/package.json /workspace/web/package.json

RUN npm install

COPY web /workspace/web

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
