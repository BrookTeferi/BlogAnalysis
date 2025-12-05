# Django Analytics API

A Django REST Framework project implementing three powerful analytics endpoints with dynamic filtering, time-series aggregation, and efficient ORM queries.

## Features

- **Three Analytics Endpoints**:
  - `/analytics/blog-views/` - Group blogs and views by country or user
  - `/analytics/top/` - Get top 10 users, countries, or blogs by views
  - `/analytics/performance/` - Time-series performance with growth metrics

- **Dynamic Filtering**: JSON-based filter system supporting AND/OR/NOT/EQ operations
- **Efficient Queries**: Optimized Django ORM with strategic database indexes
- **Time-Series Support**: Month/week/day/year aggregation and comparison

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Generate Sample Data

```bash
python manage.py generate_sample_data
```

This creates:
- 10 countries
- 50 users
- 200 blogs
- 5000+ blog views (spanning the past year)

### 4. Start Development Server

```bash
python manage.py runserver
```

### 5. Access Swagger UI

Open your browser and go to:
- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/

The Swagger UI provides interactive API documentation where you can:
- View all available endpoints
- See parameter descriptions and examples
- Test APIs directly from your browser
- View response schemas

### 6. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

Access admin at: http://127.0.0.1:8000/admin/

## Testing with Swagger UI

The easiest way to test the APIs is through the interactive Swagger UI:

1. **Start the server**: `python manage.py runserver`
2. **Open Swagger UI**: http://127.0.0.1:8000/api/docs/
3. **Select an endpoint** from the list
4. **Click "Try it out"**
5. **Fill in parameters** (use dropdown menus for enums)
6. **Click "Execute"** to see the response

**Example Test Scenarios**:
- Blog Views by Country (Month): `object_type=country`, `range=month`
- Top 10 Users (Year): `top=user`, `range=year`
- Performance Monthly: `compare=month`

## API Documentation

### API #1: Blog Views Grouping

**Endpoint**: `/analytics/blog-views/`

**Parameters**:
- `object_type` (required): `country` or `user`
- `range` (required): `month`, `week`, or `year`
- `filters` (optional): JSON filter object

**Example**:
```
GET /analytics/blog-views/?object_type=country&range=month
```

**Response**:
```json
[
  {
    "x": "United States",
    "y": 45,
    "z": 1250
  }
]
```
- `x`: Country name or username
- `y`: Number of blogs
- `z`: Total views

### API #2: Top 10 Rankings

**Endpoint**: `/analytics/top/`

**Parameters**:
- `top` (required): `user`, `country`, or `blog`
- `range` (optional): `month`, `week`, or `year`
- `filters` (optional): JSON filter object

**Example**:
```
GET /analytics/top/?top=user&range=year
```

**Response** (varies by type):
```json
[
  {
    "x": "john_doe",
    "y": "United States",
    "z": 523
  }
]
```

### API #3: Performance Time-Series

**Endpoint**: `/analytics/performance/`

**Parameters**:
- `compare` (required): `month`, `week`, `day`, or `year`
- `user_id` (optional): Specific user ID (defaults to all users)
- `filters` (optional): JSON filter object

**Example**:
```
GET /analytics/performance/?compare=month
```

**Response**:
```json
[
  {
    "x": "2024-01 (15 blogs)",
    "y": 3500,
    "z": "+12.5%"
  }
]
```
- `x`: Period label with blog count
- `y`: Total views in period
- `z`: Growth/decline vs previous period

## Dynamic Filtering

All endpoints support dynamic filtering via the `filters` parameter.

**Filter Syntax**:
```json
{
  "and": [
    {"eq": {"country__code": "US"}},
    {"or": [
      {"eq": {"blog__title__icontains": "tech"}},
      {"not": {"eq": {"viewer__is_active": false}}}
    ]}
  ]
}
```

**Supported Operations**:
- `and`: Combine conditions with AND
- `or`: Combine conditions with OR
- `not`: Negate a condition
- `eq`: Equality check (supports Django field lookups)

**Example Usage**:
```bash
# URL encode the JSON filter
GET /analytics/blog-views/?object_type=country&range=month&filters={"eq":{"country__code":"US"}}
```

## Project Structure

```
ANA/
├── ana_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── blog_analytics/            # Main analytics app
│   ├── models.py         # Country, User, Blog, BlogView
│   ├── views.py          # Three API endpoints
│   ├── filters.py        # Dynamic filtering system
│   ├── utils.py          # Helper functions
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # URL routing
│   └── management/
│       └── commands/
│           └── generate_sample_data.py
├── manage.py
└── requirements.txt
```

## Database Models

- **Country**: Country information (name, code)
- **User**: Extended Django user with country relationship
- **Blog**: Blog posts with author and metadata
- **BlogView**: Individual view tracking with timestamp and viewer

All models include strategic indexes for optimal query performance.

## Development

### Run Tests
```bash
python manage.py test analytics
```

### Check Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Access Django Shell
```bash
python manage.py shell
```

## Performance Notes

- All queries use Django ORM aggregation (no N+1 queries)
- Strategic database indexes on frequently queried fields
- Efficient use of `annotate()`, `values()`, and `Count()`
- Time-series queries use Django's `Trunc` functions

## License

MIT License
