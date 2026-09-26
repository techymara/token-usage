// 30 congressional leadership members, 119th Congress (2025–2027).
//
// Roles reflect leadership as of the start of the 119th Congress. Verify
// against congress.gov / senate.gov / house.gov before relying on this in
// production — leadership posts change mid-Congress.
//
// Headshots come from the public-domain unitedstates/images project, keyed by
// Bioguide ID. `media` values are carried over from the v3 dashboard where
// that member already had them; everyone else is null until the ingest
// pipeline fills them in.

const headshot = (bioguideId) =>
  `https://theunitedstates.io/images/congress/450x550/${bioguideId}.jpg`;

const sen = (m) => ({ chamber: 'Senate', district: null, media: null, ...m, headshot: headshot(m.bioguideId) });
const rep = (m) => ({ chamber: 'House', media: null, ...m, headshot: headshot(m.bioguideId) });

const MEMBERS = [
  // ── SENATE · Tier 1 ──
  sen({ id: 'thune', bioguideId: 'T000250', name: 'Sen. John Thune', firstName: 'John', lastName: 'Thune', initial: 'JT',
    party: 'Republican', state: 'South Dakota', stateCode: 'SD', since: 2005, leadershipTier: 1,
    leadershipRoles: ['Senate Majority Leader'], committees: ['Finance', 'Commerce, Science & Transportation'] }),
  sen({ id: 'schumer', bioguideId: 'S000148', name: 'Sen. Chuck Schumer', firstName: 'Chuck', lastName: 'Schumer', initial: 'CS',
    party: 'Democrat', state: 'New York', stateCode: 'NY', since: 1999, leadershipTier: 1,
    leadershipRoles: ['Senate Minority Leader'], committees: ['Rules & Administration'] }),

  // ── SENATE · Tier 2 ──
  sen({ id: 'barrasso', bioguideId: 'B001261', name: 'Sen. John Barrasso', firstName: 'John', lastName: 'Barrasso', initial: 'JB',
    party: 'Republican', state: 'Wyoming', stateCode: 'WY', since: 2007, leadershipTier: 2,
    leadershipRoles: ['Senate Majority Whip'], committees: ['Finance', 'Energy & Natural Resources', 'Foreign Relations'] }),
  sen({ id: 'cotton', bioguideId: 'C001095', name: 'Sen. Tom Cotton', firstName: 'Tom', lastName: 'Cotton', initial: 'TC',
    party: 'Republican', state: 'Arkansas', stateCode: 'AR', since: 2015, leadershipTier: 2,
    leadershipRoles: ['Senate Republican Conference Chair', 'Intelligence Committee Chair'],
    committees: ['Intelligence (Chair)', 'Armed Services', 'Judiciary'] }),
  sen({ id: 'capito', bioguideId: 'C001047', name: 'Sen. Shelley Moore Capito', firstName: 'Shelley Moore', lastName: 'Capito', initial: 'SC',
    party: 'Republican', state: 'West Virginia', stateCode: 'WV', since: 2015, leadershipTier: 2,
    leadershipRoles: ['Senate Republican Policy Committee Chair', 'Environment & Public Works Committee Chair'],
    committees: ['Environment & Public Works (Chair)', 'Appropriations', 'Commerce, Science & Transportation'] }),
  sen({ id: 'lankford', bioguideId: 'L000575', name: 'Sen. James Lankford', firstName: 'James', lastName: 'Lankford', initial: 'JL',
    party: 'Republican', state: 'Oklahoma', stateCode: 'OK', since: 2015, leadershipTier: 2,
    leadershipRoles: ['Senate Republican Conference Vice Chair'], committees: ['Finance', 'Homeland Security & Governmental Affairs', 'Intelligence'] }),
  sen({ id: 'grassley', bioguideId: 'G000386', name: 'Sen. Chuck Grassley', firstName: 'Chuck', lastName: 'Grassley', initial: 'CG',
    party: 'Republican', state: 'Iowa', stateCode: 'IA', since: 1981, leadershipTier: 2,
    leadershipRoles: ['President pro tempore', 'Judiciary Committee Chair'], committees: ['Judiciary (Chair)', 'Finance', 'Budget'] }),
  sen({ id: 'tim-scott', bioguideId: 'S001184', name: 'Sen. Tim Scott', firstName: 'Tim', lastName: 'Scott', initial: 'TS',
    party: 'Republican', state: 'South Carolina', stateCode: 'SC', since: 2013, leadershipTier: 2,
    leadershipRoles: ['NRSC Chair', 'Banking Committee Chair'], committees: ['Banking, Housing & Urban Affairs (Chair)', 'Finance'] }),
  sen({ id: 'durbin', bioguideId: 'D000563', name: 'Sen. Dick Durbin', firstName: 'Dick', lastName: 'Durbin', initial: 'DD',
    party: 'Democrat', state: 'Illinois', stateCode: 'IL', since: 1997, leadershipTier: 2,
    leadershipRoles: ['Senate Minority Whip', 'Judiciary Committee Ranking Member'], committees: ['Judiciary (Ranking)', 'Appropriations'] }),
  sen({ id: 'klobuchar', bioguideId: 'K000367', name: 'Sen. Amy Klobuchar', firstName: 'Amy', lastName: 'Klobuchar', initial: 'AK',
    party: 'Democrat', state: 'Minnesota', stateCode: 'MN', since: 2007, leadershipTier: 2,
    leadershipRoles: ['Senate Democratic Steering & Policy Committee Chair'], committees: ['Agriculture (Ranking)', 'Judiciary', 'Commerce, Science & Transportation'] }),
  sen({ id: 'booker', bioguideId: 'B001288', name: 'Sen. Cory Booker', firstName: 'Cory', lastName: 'Booker', initial: 'CB',
    party: 'Democrat', state: 'New Jersey', stateCode: 'NJ', since: 2013, leadershipTier: 2,
    leadershipRoles: ['Senate Democratic Strategic Communications Committee Chair'], committees: ['Judiciary', 'Foreign Relations', 'Agriculture'] }),

  // ── SENATE · Tier 3 ──
  sen({ id: 'cruz', bioguideId: 'C001098', name: 'Sen. Ted Cruz', firstName: 'Ted', lastName: 'Cruz', initial: 'TC',
    party: 'Republican', state: 'Texas', stateCode: 'TX', since: 2013, leadershipTier: 3,
    leadershipRoles: ['Commerce Committee Chair'], committees: ['Commerce, Science & Transportation (Chair)', 'Judiciary', 'Foreign Relations'],
    media: { reach: 91, vol: 88, sent: '+0.42' } }),
  sen({ id: 'paul', bioguideId: 'P000603', name: 'Sen. Rand Paul', firstName: 'Rand', lastName: 'Paul', initial: 'RP',
    party: 'Republican', state: 'Kentucky', stateCode: 'KY', since: 2011, leadershipTier: 3,
    leadershipRoles: ['Homeland Security & Governmental Affairs Committee Chair'],
    committees: ['Homeland Security & Governmental Affairs (Chair)', 'Health, Education, Labor & Pensions', 'Foreign Relations'],
    media: { reach: 68, vol: 77, sent: '+0.39' } }),
  sen({ id: 'collins', bioguideId: 'C001035', name: 'Sen. Susan Collins', firstName: 'Susan', lastName: 'Collins', initial: 'SC',
    party: 'Republican', state: 'Maine', stateCode: 'ME', since: 1997, leadershipTier: 3,
    leadershipRoles: ['Appropriations Committee Chair'], committees: ['Appropriations (Chair)', 'Health, Education, Labor & Pensions', 'Intelligence'] }),
  sen({ id: 'cantwell', bioguideId: 'C000127', name: 'Sen. Maria Cantwell', firstName: 'Maria', lastName: 'Cantwell', initial: 'MC',
    party: 'Democrat', state: 'Washington', stateCode: 'WA', since: 2001, leadershipTier: 3,
    leadershipRoles: ['Commerce Committee Ranking Member'], committees: ['Commerce, Science & Transportation (Ranking)', 'Energy & Natural Resources', 'Finance'],
    media: { reach: 84, vol: 72, sent: '+0.61' } }),
  sen({ id: 'warren', bioguideId: 'W000817', name: 'Sen. Elizabeth Warren', firstName: 'Elizabeth', lastName: 'Warren', initial: 'EW',
    party: 'Democrat', state: 'Massachusetts', stateCode: 'MA', since: 2013, leadershipTier: 3,
    leadershipRoles: ['Banking Committee Ranking Member'], committees: ['Banking, Housing & Urban Affairs (Ranking)', 'Finance', 'Armed Services'],
    media: { reach: 76, vol: 71, sent: '+0.58' } }),

  // ── HOUSE · Tier 1 ──
  rep({ id: 'johnson', bioguideId: 'J000299', name: 'Speaker Mike Johnson', firstName: 'Mike', lastName: 'Johnson', initial: 'MJ',
    party: 'Republican', state: 'Louisiana', stateCode: 'LA', district: 4, since: 2017, leadershipTier: 1,
    leadershipRoles: ['Speaker of the House'], committees: [] }),
  rep({ id: 'scalise', bioguideId: 'S000583', name: 'Rep. Steve Scalise', firstName: 'Steve', lastName: 'Scalise', initial: 'SS',
    party: 'Republican', state: 'Louisiana', stateCode: 'LA', district: 1, since: 2008, leadershipTier: 1,
    leadershipRoles: ['House Majority Leader'], committees: [] }),
  rep({ id: 'jeffries', bioguideId: 'J000294', name: 'Rep. Hakeem Jeffries', firstName: 'Hakeem', lastName: 'Jeffries', initial: 'HJ',
    party: 'Democrat', state: 'New York', stateCode: 'NY', district: 8, since: 2013, leadershipTier: 1,
    leadershipRoles: ['House Minority Leader'], committees: [] }),

  // ── HOUSE · Tier 2 ──
  rep({ id: 'emmer', bioguideId: 'E000294', name: 'Rep. Tom Emmer', firstName: 'Tom', lastName: 'Emmer', initial: 'TE',
    party: 'Republican', state: 'Minnesota', stateCode: 'MN', district: 6, since: 2015, leadershipTier: 2,
    leadershipRoles: ['House Majority Whip'], committees: ['Financial Services'] }),
  rep({ id: 'mcclain', bioguideId: 'M001136', name: 'Rep. Lisa McClain', firstName: 'Lisa', lastName: 'McClain', initial: 'LM',
    party: 'Republican', state: 'Michigan', stateCode: 'MI', district: 9, since: 2021, leadershipTier: 2,
    leadershipRoles: ['House Republican Conference Chair'], committees: ['Oversight & Government Reform'] }),
  rep({ id: 'clark', bioguideId: 'C001101', name: 'Rep. Katherine Clark', firstName: 'Katherine', lastName: 'Clark', initial: 'KC',
    party: 'Democrat', state: 'Massachusetts', stateCode: 'MA', district: 5, since: 2013, leadershipTier: 2,
    leadershipRoles: ['House Minority Whip'], committees: [] }),
  rep({ id: 'aguilar', bioguideId: 'A000371', name: 'Rep. Pete Aguilar', firstName: 'Pete', lastName: 'Aguilar', initial: 'PA',
    party: 'Democrat', state: 'California', stateCode: 'CA', district: 33, since: 2015, leadershipTier: 2,
    leadershipRoles: ['House Democratic Caucus Chair'], committees: ['Appropriations'] }),
  rep({ id: 'lieu', bioguideId: 'L000582', name: 'Rep. Ted Lieu', firstName: 'Ted', lastName: 'Lieu', initial: 'TL',
    party: 'Democrat', state: 'California', stateCode: 'CA', district: 36, since: 2015, leadershipTier: 2,
    leadershipRoles: ['House Democratic Caucus Vice Chair'], committees: ['Judiciary', 'Science, Space & Technology'] }),
  rep({ id: 'delbene', bioguideId: 'D000617', name: 'Rep. Suzan DelBene', firstName: 'Suzan', lastName: 'DelBene', initial: 'SD',
    party: 'Democrat', state: 'Washington', stateCode: 'WA', district: 1, since: 2012, leadershipTier: 2,
    leadershipRoles: ['DCCC Chair'], committees: ['Ways & Means'] }),

  // ── HOUSE · Tier 3 ──
  rep({ id: 'jordan', bioguideId: 'J000289', name: 'Rep. Jim Jordan', firstName: 'Jim', lastName: 'Jordan', initial: 'JJ',
    party: 'Republican', state: 'Ohio', stateCode: 'OH', district: 4, since: 2007, leadershipTier: 3,
    leadershipRoles: ['Judiciary Committee Chair'], committees: ['Judiciary (Chair)'],
    media: { reach: 78, vol: 84, sent: '+0.38' } }),
  rep({ id: 'jason-smith', bioguideId: 'S001195', name: 'Rep. Jason Smith', firstName: 'Jason', lastName: 'Smith', initial: 'JS',
    party: 'Republican', state: 'Missouri', stateCode: 'MO', district: 8, since: 2013, leadershipTier: 3,
    leadershipRoles: ['Ways & Means Committee Chair'], committees: ['Ways & Means (Chair)'] }),
  rep({ id: 'cole', bioguideId: 'C001053', name: 'Rep. Tom Cole', firstName: 'Tom', lastName: 'Cole', initial: 'TC',
    party: 'Republican', state: 'Oklahoma', stateCode: 'OK', district: 4, since: 2003, leadershipTier: 3,
    leadershipRoles: ['Appropriations Committee Chair'], committees: ['Appropriations (Chair)'] }),
  rep({ id: 'comer', bioguideId: 'C001108', name: 'Rep. James Comer', firstName: 'James', lastName: 'Comer', initial: 'JC',
    party: 'Republican', state: 'Kentucky', stateCode: 'KY', district: 1, since: 2016, leadershipTier: 3,
    leadershipRoles: ['Oversight & Government Reform Committee Chair'], committees: ['Oversight & Government Reform (Chair)', 'Education & Workforce'] }),
  rep({ id: 'guthrie', bioguideId: 'G000558', name: 'Rep. Brett Guthrie', firstName: 'Brett', lastName: 'Guthrie', initial: 'BG',
    party: 'Republican', state: 'Kentucky', stateCode: 'KY', district: 2, since: 2009, leadershipTier: 3,
    leadershipRoles: ['Energy & Commerce Committee Chair'], committees: ['Energy & Commerce (Chair)'] }),
];

module.exports = { MEMBERS };
