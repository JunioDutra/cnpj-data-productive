FROM node:18-alpine as builder

WORKDIR /app

COPY package.json .
COPY yarn.lock .

# RUN npm install -g yarn
RUN yarn install

FROM node:18-alpine as runner

WORKDIR /app

COPY --from=builder /app /app

COPY . .

CMD ["node", "app.js"]