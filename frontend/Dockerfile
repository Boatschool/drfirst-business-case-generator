FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port 4000 to match docker-compose
EXPOSE 4000

# Start development server on port 4000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4000"] 