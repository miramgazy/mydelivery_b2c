# Этап 1: Development (для разработки)
FROM node:20-slim as development

WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN rm -f package-lock.json && npm install

# Копируем остальные файлы
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Этап 2: Сборка
FROM node:20-slim as build

WORKDIR /app

# Принимаем аргументы для Vite (Coolify передаст их автоматически)
ARG VITE_API_URL=/api
ARG VITE_DEV_MODE=false

# Устанавливаем как ENV для Vite (Vite требует ENV переменные, начинающиеся с VITE_)
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_DEV_MODE=${VITE_DEV_MODE}

# Копируем только файлы зависимостей
COPY package*.json ./

# Очистка и установка (защита от конфликтов платформ mac/linux)
RUN rm -f package-lock.json && npm install

# Теперь можно установить NODE_ENV
ENV NODE_ENV=production

# Копируем остальные файлы и собираем
COPY . .
RUN npm run build

# Этап 3: Финальный образ с Nginx
FROM nginx:alpine as production

# Копируем собранные файлы из этапа build
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем конфиг nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]