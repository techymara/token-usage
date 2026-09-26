const { test, before, after } = require('node:test');
const assert = require('node:assert');
const app = require('../src/app');

let server;
let base;

before(async () => {
  server = app.listen(0);
  await new Promise((r) => server.once('listening', r));
  base = `http://localhost:${server.address().port}`;
});

after(() => server.close());

const get = async (path) => {
  const res = await fetch(base + path);
  return { status: res.status, body: await res.json(), headers: res.headers };
};

test('GET /members returns all 30, tier-sorted', async () => {
  const { status, body } = await get('/members');
  assert.strictEqual(status, 200);
  assert.strictEqual(body.count, 30);
  const tiers = body.members.map((m) => m.leadershipTier);
  assert.deepStrictEqual(tiers, [...tiers].sort());
  assert.ok(body.members.every((m) => m.leadershipTierLabel));
});

test('GET /members filters combine', async () => {
  const { body } = await get('/members?chamber=senate&party=democrat&tier=1');
  assert.deepStrictEqual(body.members.map((m) => m.id), ['schumer']);
});

test('GET /members?q= searches roles and committees', async () => {
  const { body } = await get('/members?q=commerce%20committee');
  assert.deepStrictEqual(body.members.map((m) => m.id).sort(), ['cantwell', 'cruz', 'guthrie']);
});

test('GET /members/:id returns one member', async () => {
  const { status, body } = await get('/members/cruz');
  assert.strictEqual(status, 200);
  assert.strictEqual(body.name, 'Sen. Ted Cruz');
  assert.strictEqual(body.media.reach, 91);
});

test('GET /members/:id 404s on unknown id', async () => {
  const { status, body } = await get('/members/nobody');
  assert.strictEqual(status, 404);
  assert.match(body.error, /nobody/);
});

test('CORS header is set', async () => {
  const { headers } = await get('/health');
  assert.strictEqual(headers.get('access-control-allow-origin'), '*');
});
