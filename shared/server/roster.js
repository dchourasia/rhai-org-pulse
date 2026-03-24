/**
 * Shared roster data access layer.
 * Reads org-roster-full.json and provides query functions
 * for use by any module that needs roster/people data.
 */

/**
 * Read the raw org-roster-full.json data.
 * @param {{ readFromStorage: Function }} storage
 * @returns {object|null}
 */
function readRosterFull(storage) {
  return storage.readFromStorage('org-roster-full.json');
}

/**
 * Get a flat array of all people across all orgs.
 * Includes the org key on each person record.
 * @param {{ readFromStorage: Function }} storage
 * @returns {object[]}
 */
function getAllPeople(storage) {
  const full = readRosterFull(storage);
  if (!full || !full.orgs) return [];
  const people = [];
  for (const [orgKey, orgData] of Object.entries(full.orgs)) {
    const allMembers = [orgData.leader, ...orgData.members];
    for (const person of allMembers) {
      people.push({ ...person, orgKey });
    }
  }
  return people;
}

/**
 * Get people in a specific org.
 * @param {{ readFromStorage: Function }} storage
 * @param {string} orgKey
 * @returns {object[]}
 */
function getPeopleByOrg(storage, orgKey) {
  const full = readRosterFull(storage);
  if (!full || !full.orgs || !full.orgs[orgKey]) return [];
  const orgData = full.orgs[orgKey];
  return [orgData.leader, ...orgData.members].map(p => ({ ...p, orgKey }));
}

/**
 * Get list of org keys with display names (leader names as fallback).
 * @param {{ readFromStorage: Function }} storage
 * @returns {{ key: string, displayName: string }[]}
 */
function getOrgKeys(storage) {
  const full = readRosterFull(storage);
  if (!full || !full.orgs) return [];
  return Object.entries(full.orgs).map(([key, orgData]) => ({
    key,
    displayName: orgData.leader?.name || key
  }));
}

module.exports = {
  readRosterFull,
  getAllPeople,
  getPeopleByOrg,
  getOrgKeys
};
