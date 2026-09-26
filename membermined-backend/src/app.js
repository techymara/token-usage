const express = require('express');
const cors = require('cors');
const { MEMBERS } = require('./data/members');
const { TIER_LABELS, validateMember } = require('./schema');

// Fail fast on bad seed data rather than serving it.
const errors = MEMBERS.flatMap(validateMember);
const ids = MEMBERS.map((m) => m.id);
ids.filter((id, i) => ids.indexOf(id) !== i).forEach((id) => errors.push(`duplicate id ${id}`));
if (errors.length) throw new Error(`Invalid member data:\n  ${errors.join('\n  ')}`);

const withTierLabel = (m) => ({ ...m, leadershipTierLabel: TIER_LABELS[m.leadershipTier] });

const app = express();
app.use(cors()); // dashboard may be opened from file:// or another port
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ ok: true, members: MEMBERS.length });
});

// GET /members?chamber=Senate&party=Democrat&tier=1&state=TX&q=cruz
app.get('/members', (req, res) => {
  const { chamber, party, tier, state, q } = req.query;
  let list = MEMBERS;
  const eq = (a, b) => String(a).toLowerCase() === String(b).toLowerCase();

  if (chamber) list = list.filter((m) => eq(m.chamber, chamber));
  if (party) list = list.filter((m) => eq(m.party, party));
  if (tier) list = list.filter((m) => m.leadershipTier === Number(tier));
  if (state) list = list.filter((m) => eq(m.stateCode, state) || eq(m.state, state));
  if (q) {
    const needle = String(q).toLowerCase();
    list = list.filter((m) =>
      [m.name, m.state, ...m.leadershipRoles, ...m.committees].some((s) => s.toLowerCase().includes(needle)));
  }

  list = [...list].sort((a, b) => a.leadershipTier - b.leadershipTier || a.lastName.localeCompare(b.lastName));
  res.json({ count: list.length, members: list.map(withTierLabel) });
});

app.get('/members/:id', (req, res) => {
  const m = MEMBERS.find((x) => x.id === req.params.id.toLowerCase());
  if (!m) return res.status(404).json({ error: `No member with id "${req.params.id}"` });
  res.json(withTierLabel(m));
});

app.use((req, res) => res.status(404).json({ error: 'Not found' }));

module.exports = app;
