FROM node:20

WORKDIR /workspace/docs

COPY docs/package.json /workspace/docs/package.json

RUN npm install

COPY docs /workspace/docs

EXPOSE 5174

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
