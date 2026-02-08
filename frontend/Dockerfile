# Frontend Dockerfile for Reflecto (static site)
# Use minimal nginx image
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/

# Copy static frontend files
COPY . /usr/share/nginx/html

# Expose port 8080
EXPOSE 8080

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]

# Set work directory
WORKDIR /frontend

# Copy static files
COPY . .

