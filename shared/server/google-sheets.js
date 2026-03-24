/**
 * Shared Google Sheets auth and raw data fetching.
 * Extracted from team-tracker's roster-sync/sheets.js for reuse by multiple modules.
 */

const { google } = require('googleapis');
const fs = require('fs');

let cachedAuth = null;

function getAuth() {
  if (cachedAuth) return cachedAuth;

  const keyFile = process.env.GOOGLE_SERVICE_ACCOUNT_KEY_FILE || '/etc/secrets/google-sa-key.json';
  if (!fs.existsSync(keyFile)) {
    throw new Error(
      `Google service account key not found at ${keyFile}. ` +
      'Set GOOGLE_SERVICE_ACCOUNT_KEY_FILE env var to the correct path.'
    );
  }

  cachedAuth = new google.auth.GoogleAuth({
    keyFile: keyFile,
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly']
  });
  return cachedAuth;
}

/**
 * Discover all sheet/tab names in a spreadsheet.
 * @param {string} sheetId - Google Spreadsheet ID
 * @returns {Promise<string[]>} Array of sheet title strings
 */
async function discoverSheetNames(sheetId) {
  const auth = getAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  const response = await sheets.spreadsheets.get({
    spreadsheetId: sheetId,
    fields: 'sheets.properties.title'
  });
  return (response.data.sheets || []).map(s => s.properties.title);
}

/**
 * Fetch raw data from a single sheet tab.
 * @param {string} sheetId - Google Spreadsheet ID
 * @param {string} sheetName - Tab name
 * @returns {Promise<{ headers: string[], rows: any[][] }>}
 */
async function fetchRawSheet(sheetId, sheetName) {
  const auth = getAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: sheetId,
    range: `'${sheetName}'`,
    valueRenderOption: 'UNFORMATTED_VALUE'
  });
  const values = response.data.values || [];
  if (values.length === 0) return { headers: [], rows: [] };
  const headers = values[0].map(h => typeof h === 'string' ? h.trim() : String(h || ''));
  return { headers, rows: values.slice(1) };
}

module.exports = {
  getAuth,
  discoverSheetNames,
  fetchRawSheet
};
