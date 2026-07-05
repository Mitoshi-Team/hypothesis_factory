FROM node:22-slim

WORKDIR /app

COPY services/frontend/package.json services/frontend/package-lock.json ./
RUN npm ci

COPY services/frontend ./
RUN npm run build

EXPOSE 4173

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]
