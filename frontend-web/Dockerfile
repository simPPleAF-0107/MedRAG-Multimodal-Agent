FROM node:18-alpine as build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Build the Vite application
RUN npm run build

# Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config if necessary, else default is usually fine for basic routing
# If React Router is used, you usually need a custom nginx config to redirect to index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
