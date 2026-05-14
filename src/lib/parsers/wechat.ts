import Papa from "papaparse";
import * as XLSX from "xlsx";
import type { ParsedTransaction, ParseResult } from "../types";

const HEADER_MARKER = "交易时间";
const BEIJING_OFFSET_MS = 8 * 60 * 60 * 1000;

// 微信列名
const COL = {
  date: "交易时间",
  direction: "收/支",
  amount: "金额(元)",
  orderId: "交易单号",
  merchant: "交易对方",
  description: "商品",
} as const;

export function parseWechatCSV(text: string, filename: string): ParseResult {
  // 整文件按行解析为 2D 数组（不带 header）
  const result = Papa.parse<string[]>(text, {
    header: false,
    skipEmptyLines: false,
  });
  return parseWechatRows(result.data, filename);
}

export function parseWechatXLSX(buffer: ArrayBuffer, filename: string): ParseResult {
  const workbook = XLSX.read(buffer, { type: "array" });
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  const rows = XLSX.utils.sheet_to_json<string[]>(sheet, {
    header: 1,
    defval: "",
    raw: false,
  });
  return parseWechatRows(rows, filename);
}

function parseWechatRows(rows: string[][], filename: string): ParseResult {
  // 找 header 行（第一列以 "交易时间" 开头）
  let headerIdx = -1;
  for (let i = 0; i < rows.length; i++) {
    const first = (rows[i]?.[0] || "").trim();
    if (first === HEADER_MARKER) {
      headerIdx = i;
      break;
    }
  }

  if (headerIdx === -1) {
    return emptyResult(filename, "未找到表头（缺少'交易时间'列）");
  }

  const header = rows[headerIdx].map((h) => (h || "").trim());
  const dataRows = rows.slice(headerIdx + 1);

  const colIdx = {
    date: header.indexOf(COL.date),
    direction: header.indexOf(COL.direction),
    amount: header.indexOf(COL.amount),
    orderId: header.indexOf(COL.orderId),
    merchant: header.indexOf(COL.merchant),
    description: header.indexOf(COL.description),
  };

  if (colIdx.date < 0 || colIdx.amount < 0 || colIdx.orderId < 0) {
    return emptyResult(filename, "缺少必要列（交易时间/金额/交易单号）");
  }

  const transactions: ParsedTransaction[] = [];
  const failedDetails: ParseResult["failedDetails"] = [];
  let skippedRows = 0;

  for (let i = 0; i < dataRows.length; i++) {
    const row = dataRows[i];
    const dataRowNum = headerIdx + 2 + i;

    // 跳过空行
    if (!row || row.every((c) => !c || !String(c).trim())) {
      skippedRows++;
      continue;
    }

    const orderId = clean(row[colIdx.orderId]);
    if (!orderId || orderId === "/") {
      skippedRows++;
      continue;
    }

    const dirRaw = clean(row[colIdx.direction]);
    if (dirRaw !== "收入" && dirRaw !== "支出") {
      skippedRows++;
      continue;
    }

    try {
      const dateStr = clean(row[colIdx.date]);
      const amountStr = clean(row[colIdx.amount]).replace(/[¥￥,\s]/g, "");

      if (!dateStr) throw new Error("缺少交易时间");
      if (!amountStr) throw new Error("缺少金额");

      const amount = Number.parseFloat(amountStr);
      if (Number.isNaN(amount)) throw new Error(`金额无法解析: ${amountStr}`);

      const date = parseBeijingDate(dateStr);
      if (!date) throw new Error(`日期无法解析: ${dateStr}`);

      const rawData: Record<string, string> = {};
      header.forEach((h, idx) => {
        if (h) rawData[h] = clean(row[idx]);
      });

      transactions.push({
        source: "wechat",
        orderId,
        transactionDate: date.toISOString(),
        amount: Math.abs(amount),
        direction: dirRaw === "收入" ? "income" : "expense",
        merchant: nullIfSlash(clean(row[colIdx.merchant])),
        description: nullIfSlash(clean(row[colIdx.description])),
        rawData,
      });
    } catch (e) {
      failedDetails.push({
        row: dataRowNum,
        reason: e instanceof Error ? e.message : "未知错误",
        data: row,
      });
    }
  }

  return {
    source: "wechat",
    filename,
    totalRows: dataRows.length,
    skippedRows,
    failedRows: failedDetails.length,
    transactions,
    failedDetails,
  };
}

function clean(v: unknown): string {
  return String(v ?? "").trim();
}

function nullIfSlash(v: string): string | null {
  return !v || v === "/" ? null : v;
}

function parseBeijingDate(s: string): Date | null {
  const m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})[\sT](\d{1,2}):(\d{1,2}):(\d{1,2})$/);
  if (!m) return null;
  const [, y, mo, d, h, mi, se] = m;
  const utcMs = Date.UTC(+y, +mo - 1, +d, +h, +mi, +se) - BEIJING_OFFSET_MS;
  return new Date(utcMs);
}

function emptyResult(filename: string, reason: string): ParseResult {
  return {
    source: "wechat",
    filename,
    totalRows: 0,
    skippedRows: 0,
    failedRows: 1,
    transactions: [],
    failedDetails: [{ row: 0, reason }],
  };
}
