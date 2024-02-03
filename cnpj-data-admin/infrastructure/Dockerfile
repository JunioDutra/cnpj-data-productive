FROM node:18-alpine as installer

WORKDIR /app

COPY package.json .
COPY yarn.lock .

RUN npm install

FROM node:18-alpine as builder

WORKDIR /app

COPY --from=installer /app /app

COPY . .

RUN npm run build

FROM node:18-alpine as runner

WORKDIR /app

COPY --from=builder /app /app

COPY . .

CMD ["npm", "run", "preview", "--", "--host"]