# Databases

Databases are internal data containers in Vortex.

They are used to define your platform data model through `tables`, `columns`, `records`, and `values`.

## What You Can Do

- Create a database.
- List databases.
- Update database metadata.
- Replace or delete a database.
- Navigate related data model resources through convenience endpoints.

## Database Fields

- `name`: Human-readable database name.
- `slug`: Stable identifier used for routing and references.

## Data Model Resources

- `tables`
- `columns`
- `records`
- `values`

## Convenience Endpoints

These return the same result set you would get by querying the child resource with the parent id filter.

- `GET /databases/{id}/tables`
- `GET /tables/{id}/columns`
- `GET /tables/{id}/records`
- `GET /columns/{id}/values`
- `GET /records/{id}/values`

## API Endpoints

- `GET /databases`
- `POST /databases`
- `GET /databases/{id}`
- `PUT /databases/{id}` (replace)
- `PATCH /databases/{id}` (update)
- `DELETE /databases/{id}`

## Notes

- Databases do not require host, port, or engine fields.
- Databases are not currently linked to applications by foreign key.
