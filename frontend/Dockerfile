# Multi-stage build для фронтенда

# Stage 1: Development
FROM node:20-alpine as development

WORKDIR /app

# Копируем package файлы
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходники
COPY . .

# Открываем порт для Vite dev server
EXPOSE 5173

# Запускаем dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]


# Stage 2: Build для production
FROM node:20-alpine as build

WORKDIR /app

# Копируем package файлы
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходники
COPY . .

# Сборка приложения
RUN npm run build


# Stage 3: Production с Nginx
FROM nginx:alpine as production

# Копируем собранное приложение
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем конфиг nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]