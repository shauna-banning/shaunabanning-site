// Home Value Leads: receives shaunabanning.com/home-value form posts.
// Step 1 adds a row + emails Shauna. Step 2 fills in the same row (matched by Lead ID) + emails the details.
var SHEET_ID = "1au70ahGLiZcY_2m8BLOKmK_tYpeaNSKVujQXmT_gHXA";
var NOTIFY = "shaunasellstampa@gmail.com";
var HEADERS = ["Lead ID","Submitted","Name","Email","Address","Source","Phone","Timeline","Beds","Baths","Pool","Upgrades","Unique Features","Delivery Notes","Details Added","Status"];

function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p.website) return ok_(); // honeypot: bots fill hidden field
  var lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    var sh = sheet_();
    var tz = "America/New_York", now = Utilities.formatDate(new Date(), tz, "yyyy-MM-dd h:mm a");
    if (p.step === "2") {
      var row = findRow_(sh, p.id);
      var vals = [p.phone||"", p.timeline||"", p.beds||"", p.baths||"", p.pool||"", p.upgrades||"", p.features||"", p.delivery_notes||"", now];
      if (row) sh.getRange(row, 7, 1, vals.length).setValues([vals]);
      else sh.appendRow([p.id||"", now, p.name||"", p.email||"", p.address||"", "(details only)"].concat(vals).concat(["New"]));
      MailApp.sendEmail({ to: NOTIFY, subject: "🔥 Home value details: " + (p.address || p.email || p.id),
        body: "Phone: " + (p.phone||"") + "\nTimeline: " + (p.timeline||"") + "\nBeds/Baths: " + (p.beds||"?") + " / " + (p.baths||"?") +
              "\nPool: " + (p.pool||"") + "\nUpgrades: " + (p.upgrades||"") + "\nUnique: " + (p.features||"") + "\nDelivery notes: " + (p.delivery_notes||"") +
              "\n\nName: " + (p.name||"") + "\nEmail: " + (p.email||"") + "\nAddress: " + (p.address||"") + "\n\nCall them now. Sheet: https://docs.google.com/spreadsheets/d/" + SHEET_ID });
    } else {
      sh.appendRow([p.id||"", now, p.name||"", p.email||"", p.address||"", p.source||"", "", "", "", "", "", "", "", "", "", "New"]);
      MailApp.sendEmail({ to: NOTIFY, subject: "🏠 New home value lead: " + (p.address || p.email),
        body: "Name: " + (p.name||"(not given)") + "\nEmail: " + (p.email||"") + "\nAddress: " + (p.address||"") + "\nSource: " + (p.source||"") +
              "\n\nThey may still add phone + details on the thank-you page.\nSheet: https://docs.google.com/spreadsheets/d/" + SHEET_ID });
    }
  } finally { lock.releaseLock(); }
  return ok_();
}

function doGet() { return ok_(); }
function ok_() { return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON); }
function sheet_() {
  var sh = SpreadsheetApp.openById(SHEET_ID).getSheets()[0];
  if (sh.getLastRow() === 0) { sh.appendRow(HEADERS); sh.setFrozenRows(1); sh.getRange(1,1,1,HEADERS.length).setFontWeight("bold"); }
  return sh;
}
function findRow_(sh, id) {
  if (!id) return 0;
  var ids = sh.getRange(1, 1, sh.getLastRow(), 1).getValues();
  for (var i = ids.length - 1; i > 0; i--) if (String(ids[i][0]) === String(id)) return i + 1;
  return 0;
}
// Run once from the editor to grant permissions (Sheets + email).
function authorize() { sheet_(); MailApp.getRemainingDailyQuota(); }
