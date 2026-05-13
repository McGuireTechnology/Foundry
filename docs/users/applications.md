# Applications

Applications are top-level containers for your product spaces in Vortex.

Use Applications to organize teams, workflows, and related resources in one place.

## What You Can Do

- Create an application.
- List existing applications.
- Update application details.
- Replace an application.
- Delete an application.

## Application Fields

- `name`: Human-readable display name.
- `slug`: Stable identifier used in URLs and API payloads.
- `description`: Optional notes about purpose and scope.

## Dashboard Workflow

1. Open the Dashboard home page.
2. Go to the `Applications` section.
3. Use `Create` to add a new application.
4. Use `Edit` to update name, slug, or description.
5. Use `Delete` to remove an application you no longer need.

## API Endpoints

- `GET /applications`
- `POST /applications`
- `GET /applications/{id}`
- `PUT /applications/{id}` (replace)
- `PATCH /applications/{id}` (update)
- `DELETE /applications/{id}`

## Notes

- `slug` values should be unique and URL-safe.
- Prefer `PATCH` for partial updates and `PUT` when replacing the full resource.
