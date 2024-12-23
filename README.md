services:
  postgres:
    image: postgres:15.1
    container_name: postgres_db
    environment:
      POSTGRES_USER: dbuser
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app
    ports:
      - "5434:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
