/**
 * Scheduler for periodic org roster data refresh.
 */

let syncInProgress = false;
let dailyTimer = null;
const TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000;

function isSyncInProgress() {
  return syncInProgress;
}

function setSyncInProgress(val) {
  syncInProgress = val;
}

/**
 * Schedule daily sync. Returns a cancel function.
 */
function scheduleDaily(syncFn) {
  if (dailyTimer) {
    clearInterval(dailyTimer);
  }

  dailyTimer = setInterval(function() {
    console.log('[org-roster] Running scheduled daily sync...');
    syncFn().catch(function(err) {
      console.error('[org-roster] Scheduled sync error:', err);
    });
  }, TWENTY_FOUR_HOURS);

  if (dailyTimer.unref) dailyTimer.unref();

  return function cancel() {
    if (dailyTimer) {
      clearInterval(dailyTimer);
      dailyTimer = null;
    }
  };
}

module.exports = {
  isSyncInProgress,
  setSyncInProgress,
  scheduleDaily
};
