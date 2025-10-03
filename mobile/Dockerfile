FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install Expo CLI globally
RUN npm install -g @expo/cli

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S expo -u 1001

# Change ownership
RUN chown -R expo:nodejs /app
USER expo

# Expose ports
EXPOSE 19000 19001 19002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:19000 || exit 1

# Start the development server
CMD ["npm", "start"]