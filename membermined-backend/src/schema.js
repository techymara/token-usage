// Member schema and validation.
//
// Leadership tiers:
//   1 = Top party leadership (Speaker, floor leaders)
//   2 = Elected leadership (whips, conference/caucus officers, campaign chairs,
//       President pro tempore)
//   3 = Committee leadership (chairs and ranking members of major committees)

const CHAMBERS = ['Senate', 'House'];
const PARTIES = ['Republican', 'Democrat', 'Independent'];
const TIERS = [1, 2, 3];

const TIER_LABELS = {
  1: 'Top Leadership',
  2: 'Elected Leadership',
  3: 'Committee Leadership',
};

// field -> [type, required]
const FIELDS = {
  id: ['string', true],             // URL-safe slug, e.g. "cruz"
  bioguideId: ['string', true],     // Congress.gov Bioguide ID, stable join key
  name: ['string', true],           // Display name with title, e.g. "Sen. Ted Cruz"
  firstName: ['string', true],
  lastName: ['string', true],
  initial: ['string', true],        // Avatar initials
  party: ['string', true],
  state: ['string', true],
  stateCode: ['string', true],
  chamber: ['string', true],
  district: ['number', false],      // House only; null for Senate
  since: ['number', true],          // Year first sworn into current chamber
  leadershipTier: ['number', true],
  leadershipRoles: ['array', true], // e.g. ["Senate Majority Leader"]
  committees: ['array', true],
  headshot: ['string', false],
  media: ['object', false],         // { reach, vol, sent } from the dashboard, when known
};

function typeOf(v) {
  if (v === null || v === undefined) return 'null';
  if (Array.isArray(v)) return 'array';
  return typeof v;
}

// Returns a list of error strings; empty list means valid.
function validateMember(m) {
  const errors = [];
  for (const [field, [type, required]] of Object.entries(FIELDS)) {
    const actual = typeOf(m[field]);
    if (actual === 'null') {
      if (required) errors.push(`${m.id || '?'}: missing ${field}`);
    } else if (actual !== type) {
      errors.push(`${m.id || '?'}: ${field} should be ${type}, got ${actual}`);
    }
  }
  if (!CHAMBERS.includes(m.chamber)) errors.push(`${m.id}: bad chamber ${m.chamber}`);
  if (!PARTIES.includes(m.party)) errors.push(`${m.id}: bad party ${m.party}`);
  if (!TIERS.includes(m.leadershipTier)) errors.push(`${m.id}: bad tier ${m.leadershipTier}`);
  if (m.chamber === 'House' && typeOf(m.district) !== 'number') {
    errors.push(`${m.id}: House member needs a district`);
  }
  if (m.id && !/^[a-z0-9-]+$/.test(m.id)) errors.push(`${m.id}: id must be a lowercase slug`);
  return errors;
}

module.exports = { CHAMBERS, PARTIES, TIERS, TIER_LABELS, FIELDS, validateMember };
