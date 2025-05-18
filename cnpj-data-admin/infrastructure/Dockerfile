FROM node:23-alpine AS installer

WORKDIR /app

COPY package.json .
COPY yarn.lock .

RUN npm install

FROM node:23-alpine AS builder

WORKDIR /app

COPY --from=installer /app /app

COPY . .

RUN npm run build

FROM node:23-alpine AS runner

WORKDIR /app

COPY --from=builder /app /app

COPY . .

CMD ["npm", "run", "preview", "--", "--host"]