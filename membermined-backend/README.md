# membermined-backend

Express API that serves congressional leadership member data to the membermined dashboard.

## Run locally

Requires Node.js 18+.

```bash
cd membermined-backend
npm install
npm start          # http://localhost:3001  (set PORT to change)
npm run dev        # same, restarts on file changes
npm test           # endpoint tests
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | `{ ok, members }` |
| GET | `/members` | All members, sorted by tier then last name. Returns `{ count, members }` |
| GET | `/members/:id` | One member by slug (e.g. `cruz`, `tim-scott`), or 404 |

`/members` query filters (all optional, combinable, case-insensitive):

- `chamber`: `Senate` or `House`
- `party`: `Republican`, `Democrat`, or `Independent`
- `tier`: `1`, `2`, or `3`
- `state`: code or name (`TX` / `Texas`)
- `q`: free text across name, state, leadership roles, and committees

Example: `GET /members?chamber=senate&tier=3`

CORS is open, so the dashboard can call the API from `file://` or any port.

## Member schema

Defined and validated in `src/schema.js`. The server won't start if the seed data is invalid.

| Field | Type | Notes |
|---|---|---|
| `id` | string | URL slug |
| `bioguideId` | string | Congress.gov Bioguide ID, the stable key for joining other data sources |
| `name`, `firstName`, `lastName`, `initial` | string | |
| `party`, `state`, `stateCode`, `chamber` | string | |
| `district` | number \| null | House only |
| `since` | number | Year first sworn into the current chamber |
| `leadershipTier` | 1 \| 2 \| 3 | See below |
| `leadershipTierLabel` | string | Added in responses |
| `leadershipRoles` | string[] | |
| `committees` | string[] | |
| `headshot` | string | Public-domain photo from the unitedstates/images project |
| `media` | `{ reach, vol, sent }` \| null | Carried over from the v3 dashboard where available |

**Leadership tiers**

1. **Top Leadership**: Speaker and the floor leaders
2. **Elected Leadership**: whips, conference and caucus officers, campaign-committee chairs, President pro tempore
3. **Committee Leadership**: chairs and ranking members of major committees

## Data

`src/data/members.js` holds 30 hardcoded members of the 119th Congress: 16 senators and 14 representatives. Roles are as of the start of the 119th Congress. Check them against congress.gov before production use.
