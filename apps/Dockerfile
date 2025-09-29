FROM node:18-alpine

WORKDIR /app

# Copy package files first for better layer caching
COPY web/package*.json ./

# Install dependencies in the image
RUN npm ci || npm install

# Copy source code (this won't overwrite node_modules due to volume mount)
COPY web/ ./

EXPOSE 3000

# Use dev server (build step not needed for development)
CMD ["npm", "run", "dev"]
