FROM node:20-alpine as build

WORKDIR /app

COPY package.json package-lock.json* bun.lock* ./
# Use npm to install to avoid needing bun if it's not present in alpine, or we can use bun image.
# Actually, the project has bun.lock. Let's install bun or just use npm.
RUN npm install --legacy-peer-deps

COPY . .

# Build the project
RUN npm run build

# Production server
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

