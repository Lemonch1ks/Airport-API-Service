# Airport API Service

Airport API Service is a REST API for managing airports, airplanes, routes, flights, crews, orders, and tickets. It supports JWT authentication, role-based access, flight search, and seat booking with validation against duplicate reservations.

![](https://media.mate.academy/airport_diagram_ce181e403f.png)

## Features

- User registration and JWT authentication
- Airport, airplane type, airplane, crew, route, and flight management
- Route filtering by source and destination airports
- Flight filtering by route, airplane, airports, and departure/arrival dates
- Orders containing one or more tickets
- Validation of airplane row and seat limits
- Protection against booking the same seat twice
- Atomic order creation and update
- User-specific orders and tickets
- Admin-only write access to airport data
- Interactive Swagger and ReDoc documentation
- PostgreSQL database
- Dockerized development environment

## Technologies

- Python 3.12
- Django 6
- Django REST Framework
- PostgreSQL 16
- Simple JWT
- drf-spectacular
- Docker and Docker Compose

## Database structure

The main relationships are:

- an `Airplane` belongs to an `AirplaneType`;
- a `Route` connects a source airport and a destination airport;
- a `Flight` belongs to a route and uses one airplane;
- a flight can have multiple crew members;
- an `Order` belongs to a user;
- an order contains one or more tickets;
- a `Ticket` reserves a row and seat on a particular flight.

The combination of flight, row, and seat is unique, so the same seat cannot be booked twice for one flight.

## Run with Docker

### 1. Clone the repository

```bash
git clone -b develop https://github.com/Lemonch1ks/Airport-API-Service.git
cd Airport-API-Service
```

### 2. Create the environment file

Create a `.env` file in the project root:

```env
POSTGRES_DB=airport
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

`POSTGRES_HOST` must be `db` when the application is started with Docker Compose because `db` is the database service name.

### 3. Build and start the containers

```bash
docker compose up --build
```

The application waits for PostgreSQL and applies migrations automatically. It will then be available at:

```text
http://127.0.0.1:8000/
```

To start the containers in the background:

```bash
docker compose up --build -d
```

To stop them:

```bash
docker compose down
```

To stop the project and remove the database volume:

```bash
docker compose down -v
```

> Removing the volume permanently deletes the local database data.

### 4. Create an administrator

```bash
docker compose exec app python manage.py createsuperuser
```

The administrator can manage all resources through the API and through Django Admin:

```text
http://127.0.0.1:8000/admin/
```

## API documentation

After starting the project, the generated documentation is available at:

| Documentation | URL |
|---|---|
| Swagger UI | `http://127.0.0.1:8000/api/schema/swagger-ui/` |
| ReDoc | `http://127.0.0.1:8000/api/schema/redoc/` |
| OpenAPI schema | `http://127.0.0.1:8000/api/schema/` |

## Authentication

### Register a user

```http
POST /api/user/register/
```

Example request:

```json
{
  "email": "user@example.com",
  "password": "strong-password"
}
```

### Obtain JWT tokens

```http
POST /api/user/token/
```

```json
{
  "email": "user@example.com",
  "password": "strong-password"
}
```

The response contains `access` and `refresh` tokens. Send the access token with protected requests:

```http
Authorization: Bearer <access-token>
```

Additional authentication endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/user/token/refresh/` | Refresh an access token |
| `POST` | `/api/user/token/verify/` | Verify a token |
| `GET`, `PUT`, `PATCH` | `/api/user/me/` | View or update the current user |

In Swagger UI, click **Authorize** and enter:

```text
Bearer <access-token>
```

## Permissions

| User | Read airport data | Modify airport data | Manage orders | View tickets |
|---|---:|---:|---:|---:|
| Anonymous | Yes | No | No | No |
| Authenticated user | Yes | No | Own orders only | Own tickets only |
| Staff/admin | Yes | Yes | All orders | All tickets |

Airport data includes airports, airplane types, airplanes, crews, routes, and flights.

## Main endpoints

All resource endpoints support detail URLs in the form `/api/airport/<resource>/<id>/`.

| Endpoint | Supported operations | Description |
|---|---|---|
| `/api/airport/airports/` | CRUD | Airports |
| `/api/airport/airplanes/types/` | CRUD | Airplane types |
| `/api/airport/airplanes/` | CRUD | Airplanes |
| `/api/airport/crews/` | CRUD | Crew members |
| `/api/airport/routes/` | CRUD | Routes between airports |
| `/api/airport/flights/` | CRUD | Flights |
| `/api/airport/orders/` | CRUD | Authenticated user's orders |
| `/api/airport/tickets/` | Read only | Tickets visible to the current user |

Write operations for airport data require a staff/admin account.

## Filtering

### Routes

Routes can be filtered by airport ID, airport name, or closest big city:

```text
/api/airport/routes/?source=London
/api/airport/routes/?destination=Paris
/api/airport/routes/?source=1&destination=2
```

### Flights

Supported flight filters:

| Parameter | Example |
|---|---|
| `route` or `route_id` | `?route=1` |
| `airplane` or `airplane_id` | `?airplane=2` |
| `source` | `?source=London` |
| `destination` | `?destination=Paris` |
| `departure_date` or `departure_time` | `?departure_date=2026-07-25` |
| `arrival_date` or `arrival_time` | `?arrival_date=2026-07-25` |

Several numeric values can be passed as a comma-separated list:

```text
/api/airport/flights/?route=1,2&airplane=1,3
```

## Create an order

Creating an order requires authentication. The user is taken from the JWT token and must not be included in the request body.

```http
POST /api/airport/orders/
Authorization: Bearer <access-token>
Content-Type: application/json
```

```json
{
  "tickets": [
    {
      "flight": 1,
      "row": 3,
      "seat": 2
    },
    {
      "flight": 1,
      "row": 3,
      "seat": 3
    }
  ]
}
```

The API rejects:

- an empty ticket list;
- duplicate seats in the same request;
- a seat already booked for the selected flight;
- rows or seats outside the airplane layout;
- rows and seats smaller than 1.

## Load test data

If `airport_test_data.json` is located in the project root, load it with:

```bash
docker compose exec app python manage.py loaddata /app/airport_test_data.json
```

Loading fixtures into an empty database is recommended to avoid primary-key or booked-seat conflicts.

## Run tests

Run the complete test suite inside the application container:

```bash
docker compose exec app python manage.py test
```

Run only the airport application tests:

```bash
docker compose exec app python manage.py test airport.tests
```

## Useful Docker commands

Open a shell inside the application container:

```bash
docker compose exec app sh
```

Open the PostgreSQL console:

```bash
docker compose exec db psql -U postgres -d airport
```

View container logs:

```bash
docker compose logs -f app
```

Apply migrations manually if needed:

```bash
docker compose exec app python manage.py migrate
```

## Project author

[Lemonch1ks](https://github.com/Lemonch1ks)
