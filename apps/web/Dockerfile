
FROM node:20-alpine
WORKDIR /app
COPY ./package.json ./pnpm-lock.yaml* ./
RUN npm i -g pnpm && pnpm install --frozen-lockfile || pnpm install
COPY . .
EXPOSE 3000
CMD ["pnpm","dev","--host","0.0.0.0","--port","3000"]
