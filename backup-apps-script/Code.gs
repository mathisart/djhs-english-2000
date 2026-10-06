/**
 * DJHS English 2000 - Supabase monthly CSV backup to Google Drive
 * Setup:
 * 1. Apps Script > Project Settings > Script properties:
 *    SUPABASE_URL = https://<project-ref>.supabase.co
 *    SUPABASE_SECRET_KEY = <Supabase secret/service_role key>
 *    BACKUP_FOLDER_ID = <Google Drive parent folder id>
 * 2. Run installMonthlyTrigger() once and authorize.
 * 3. Run backupNow() once for a test backup.
 */
const CFG = {
  pageSize: 1000,
  timezone: "Asia/Taipei",
  folderPrefix: "DJHS-English-2000",
  logFile: "backup-log.csv",
  tables: [
    { name: "players", order: "created_at.asc" },
    { name: "learning_events", order: "id.asc" }
  ]
};

function props_() {
  const p = PropertiesService.getScriptProperties();
  const out = {
    url: (p.getProperty("SUPABASE_URL") || "").replace(/\/$/, ""),
    key: p.getProperty("SUPABASE_SECRET_KEY") || "",
    folderId: p.getProperty("BACKUP_FOLDER_ID") || ""
  };
  if (!out.url || !out.key || !out.folderId) {
    throw new Error("Missing SUPABASE_URL, SUPABASE_SECRET_KEY or BACKUP_FOLDER_ID in Script Properties.");
  }
  return out;
}

function backupNow() {
  const started = new Date();
  let monthFolder = null;
  try {
    const p = props_();
    const root = DriveApp.getFolderById(p.folderId);
    const month = Utilities.formatDate(started, CFG.timezone, "yyyy-MM");
    monthFolder = getOrCreateFolder_(root, month);
    const stamp = Utilities.formatDate(started, CFG.timezone, "yyyyMMdd-HHmmss");

    let totalRows = 0;
    CFG.tables.forEach(t => {
      const rows = fetchAll_(p, t.name, t.order);
      totalRows += rows.length;
      const csv = toCsv_(rows);
      const blob = Utilities.newBlob("\uFEFF" + csv, "text/csv;charset=UTF-8", t.name + "-" + stamp + ".csv");
      monthFolder.createFile(blob);
    });

    writeManifest_(monthFolder, stamp, started, totalRows, "SUCCESS", "");
    appendLog_(root, started, "SUCCESS", month, totalRows, "");
    return { ok: true, month: month, rows: totalRows };
  } catch (err) {
    try {
      const p = props_();
      const root = DriveApp.getFolderById(p.folderId);
      const month = Utilities.formatDate(started, CFG.timezone, "yyyy-MM");
      appendLog_(root, started, "FAILED", month, 0, String(err && err.stack || err));
      if (monthFolder) writeManifest_(monthFolder, Utilities.formatDate(started, CFG.timezone, "yyyyMMdd-HHmmss"), started, 0, "FAILED", String(err));
    } catch (_) {}
    throw err;
  }
}

function fetchAll_(p, table, order) {
  const all = [];
  let from = 0;
  while (true) {
    const to = from + CFG.pageSize - 1;
    const url = p.url + "/rest/v1/" + encodeURIComponent(table) +
      "?select=*&order=" + encodeURIComponent(order);
    const res = UrlFetchApp.fetch(url, {
      method: "get",
      headers: {
        apikey: p.key,
        Authorization: "Bearer " + p.key,
        Range: from + "-" + to,
        Prefer: "count=exact"
      },
      muteHttpExceptions: true
    });
    const code = res.getResponseCode();
    if (code < 200 || code >= 300) throw new Error(table + " HTTP " + code + ": " + res.getContentText().slice(0, 500));
    const rows = JSON.parse(res.getContentText() || "[]");
    all.push.apply(all, rows);
    if (rows.length < CFG.pageSize) break;
    from += CFG.pageSize;
    Utilities.sleep(100);
  }
  return all;
}

function toCsv_(rows) {
  if (!rows.length) return "no_data\r\n";
  const headers = Array.from(rows.reduce((s, r) => { Object.keys(r).forEach(k => s.add(k)); return s; }, new Set()));
  const esc = v => {
    if (v === null || v === undefined) return "";
    const s = typeof v === "object" ? JSON.stringify(v) : String(v);
    return '"' + s.replace(/"/g, '""') + '"';
  };
  return [headers.map(esc).join(",")]
    .concat(rows.map(r => headers.map(h => esc(r[h])).join(",")))
    .join("\r\n") + "\r\n";
}

function getOrCreateFolder_(parent, name) {
  const it = parent.getFoldersByName(name);
  return it.hasNext() ? it.next() : parent.createFolder(name);
}

function writeManifest_(folder, stamp, started, rows, status, error) {
  const data = {
    system: CFG.folderPrefix,
    backup_started_at: started.toISOString(),
    backup_finished_at: new Date().toISOString(),
    timezone: CFG.timezone,
    status: status,
    total_rows: rows,
    error: error || ""
  };
  folder.createFile("manifest-" + stamp + ".json", JSON.stringify(data, null, 2), MimeType.PLAIN_TEXT);
}

function appendLog_(root, date, status, month, rows, error) {
  const header = "\uFEFFtimestamp,status,month,total_rows,error\r\n";
  const line = [date.toISOString(), status, month, rows, String(error || "").replace(/[\r\n]+/g, " ")]
    .map(v => '"' + String(v).replace(/"/g, '""') + '"').join(",") + "\r\n";
  const it = root.getFilesByName(CFG.logFile);
  if (!it.hasNext()) {
    root.createFile(Utilities.newBlob(header + line, "text/csv;charset=UTF-8", CFG.logFile));
  } else {
    const f = it.next();
    const old = f.getBlob().getDataAsString("UTF-8").replace(/^\uFEFF?/, "");
    f.setContent("\uFEFF" + old + line);
  }
}

function installMonthlyTrigger() {
  deleteBackupTriggers_();
  ScriptApp.newTrigger("backupNow")
    .timeBased()
    .onMonthDay(1)
    .atHour(3)
    .inTimezone(CFG.timezone)
    .create();
}

function deleteBackupTriggers_() {
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === "backupNow") ScriptApp.deleteTrigger(t);
  });
}

function testConnection() {
  const p = props_();
  return CFG.tables.map(t => ({ table: t.name, rows: fetchAll_(p, t.name, t.order).length }));
}
