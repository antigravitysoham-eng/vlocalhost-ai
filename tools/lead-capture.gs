/**
 * Vlocalhost.AI — lead capture into a Google Sheet.
 *
 * The site is static, so it has nowhere to write. This is the receiving end:
 * a Google Apps Script published as a web app, which appends each submission
 * to a sheet you own and emails you a copy.
 *
 * ── SETUP (about ten minutes, once) ─────────────────────────────────────────
 *
 *  1. Sign in to Google as vlocalhostai@gmail.com.
 *  2. Create a new spreadsheet: https://sheets.new — name it "Vlocalhost leads".
 *  3. In that sheet: Extensions → Apps Script. Delete the sample code.
 *  4. Paste this whole file in. Save (the project name does not matter).
 *  5. Deploy → New deployment → gear icon → Web app.
 *       Description:  lead capture
 *       Execute as:   Me (vlocalhostai@gmail.com)
 *       Who has access: **Anyone**        ← required; visitors are not signed in
 *  6. Deploy. Google asks you to authorise it — Advanced → Go to project
 *     (unsafe) is expected for your own script. Allow.
 *  7. Copy the Web app URL. It looks like
 *       https://script.google.com/macros/s/AKfy…long…/exec
 *  8. Send me that URL and I will wire it into the two pages that have the
 *     form, or paste it yourself into LEAD_ENDPOINT in index.html and
 *     pricing/index.html.
 *
 * ── AFTER ANY EDIT ──────────────────────────────────────────────────────────
 * Deploy → Manage deployments → edit → Version: New version → Deploy.
 * Editing the code alone changes nothing that is live.
 *
 * ── NOTES ───────────────────────────────────────────────────────────────────
 * The page posts as text/plain on purpose. A JSON content type turns the
 * request into a CORS preflight, which Apps Script does not answer, and the
 * lead is lost with a console error the visitor never sees. Simple request,
 * no preflight, no CORS.
 */

/** Where a copy of each lead is emailed. Empty string turns email off. */
var NOTIFY = 'vlocalhostai@gmail.com';

/**
 * The spreadsheet to write into, by id — the long string in its URL between
 * /d/ and /edit.
 *
 * A script created from Extensions → Apps Script is bound to its sheet and
 * needs none of this. With two Google accounts signed into one browser, that
 * binding fails to open ("unable to open the file at present"), so this runs
 * as a standalone project instead and names the sheet explicitly. Leave the
 * string empty in a bound script and the active spreadsheet is used.
 */
var SHEET_ID = '1_9WqBBEILsi2Jmn4o-2mCjR6LM9-317y3BH0onrm3gs';

/** Tab within the spreadsheet. Created on first use. */
var TAB = 'Leads';

var HEADERS = ['Received', 'Name', 'Email', 'Phone', 'Company',
               'Consented', 'Page', 'Source'];

function book_() {
  return SHEET_ID ? SpreadsheetApp.openById(SHEET_ID)
                  : SpreadsheetApp.getActiveSpreadsheet();
}

function sheet_() {
  var book = book_();
  var tab = book.getSheetByName(TAB) || book.insertSheet(TAB);
  if (tab.getLastRow() === 0) {
    tab.appendRow(HEADERS);
    tab.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    tab.setFrozenRows(1);
  }
  return tab;
}

function doPost(e) {
  try {
    var raw = (e && e.postData && e.postData.contents) || '{}';
    var d = JSON.parse(raw);

    // A submission with no email is either a bot or a mis-fire; either way it
    // is not a lead, and letting it through only dilutes the sheet.
    var email = String(d.email || '').trim();
    if (!email) {
      return reply_({ ok: false, error: 'no email' });
    }

    var row = [
      new Date(),
      String(d.name || '').trim(),
      email,
      String(d.phone || '').trim(),
      String(d.company || '').trim(),
      d.consent ? 'yes' : 'no',
      String(d.page || '').trim(),
      String(d.source || 'website').trim()
    ];
    sheet_().appendRow(row);

    if (NOTIFY) {
      MailApp.sendEmail({
        to: NOTIFY,
        subject: 'Vlocalhost lead — ' + (row[1] || email),
        body: [
          'Name:     ' + row[1],
          'Email:    ' + row[2],
          'Phone:    ' + row[3],
          'Company:  ' + row[4],
          'Consent:  ' + row[5],
          'Page:     ' + row[6],
          '',
          'Sheet: ' + book_().getUrl()
        ].join('\n')
      });
    }
    return reply_({ ok: true });
  } catch (err) {
    // Never fail loudly: the visitor is already being sent to the download,
    // and a 500 here would only show up as a broken-looking site.
    console.error(err);
    return reply_({ ok: false, error: String(err) });
  }
}

/** Visiting the URL in a browser should say something useful. */
function doGet() {
  return reply_({
    ok: true,
    service: 'vlocalhost lead capture',
    rows: Math.max(0, sheet_().getLastRow() - 1)
  });
}

function reply_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
