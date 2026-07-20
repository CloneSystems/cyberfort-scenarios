FROM node:18-bullseye-slim
WORKDIR /srv/netlink

COPY package.json ./
RUN npm install --no-audit --no-fund

COPY server.js ./
COPY src ./src
COPY views ./views

ENV NODE_ENV=development
EXPOSE 3000
CMD ["node", "server.js"]
