# Production Dockerfile for Pulse of People Frontend
# Simplified single-stage build for Render deployment

FROM node:22-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY frontend/ ./

# Build production bundle
RUN npm run build

# Install serve to host the static files
RUN npm install -g serve

# Expose port (Render will assign this dynamically)
EXPOSE 3000

# Serve the built files
CMD ["serve", "-s", "dist", "-l", "3000"]
