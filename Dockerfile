# ---------- FRONTEND BUILD ----------
FROM node:18 as frontend-build

WORKDIR /frontend
COPY frontend/ .
RUN npm install
RUN npm run build

# ---------- BACKEND ----------
FROM python:3.10

WORKDIR /app

# copy backend
COPY backend/ .

# install python deps
RUN pip install -r requirements.txt

# copy frontend build into backend
COPY --from=frontend-build /frontend/build ./static

# run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]