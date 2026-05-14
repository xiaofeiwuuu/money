import Papa from "papaparse";
import type { ParsedTransaction, ParseResult } from "../types";

const HEADER_MARKER = "交易时间";
const BEIJING_OFFSET_MS = 8 * 60 * 60 * 1000;

// 支付宝列名
const COL = {
  date: "交易时间",
  direction: "收/支",
  amount: "金额",
  orderId: "交易订单号",
  merchant: "交易对方",
  description: "商品说明",
} as const;

interface RawRow {
  [key: string]: string;
}

export function parseAlipay(text: string, filename: string): ParseResult {
  const lines = text.split(/\r?\n/);

  // 找到 header 行（以 "交易时间,..." 开头）
  let headerIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith(HEADER_MARKER)) {
      headerIdx = i;
      break;
    }
  }

  if (headerIdx === -1) {
    return emptyResult(filename, "未找到表头（缺少'交易时间'列）");
  }

  // 截取 header + data 部分
  const csvBlock = lines.slice(headerIdx).join("\n");

  // 末尾通常有空行或备注，先尝试 papaparse 全部解析，过滤掉非数据行
  const parsed = Papa.parse<RawRow>(csvBlock, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (h) => h.trim(),
  });

  const transactions: ParsedTransaction[] = [];
  const failedDetails: ParseResult["failedDetails"] = [];
  let skippedRows = 0;

  for (let i = 0; i < parsed.data.length; i++) {
    const row = parsed.data[i];
    const dataRowNum = headerIdx + 2 + i; // CSV 行号（1-based + header）

    // 跳过没有订单号的行（备注尾行等）
    // 支付宝单元格末尾常有 \t 制表符，要清掉
    const orderIdRaw = clean(row[COL.orderId]);
    if (!orderIdRaw) {
      skippedRows++;
      continue;
    }

    const dirRaw = (row[COL.direction] || "").trim();
    // 跳过 "不计收支" 这类（V0 不导入资金转移）
    if (dirRaw !== "收入" && dirRaw !== "支出") {
      skippedRows++;
      continue;
    }

    try {
      const tx = buildTransaction(row, "alipay");
      transactions.push(tx);
    } catch (e) {
      failedDetails.push({
        row: dataRowNum,
        reason: e instanceof Error ? e.message : "未知错误",
        data: row,
      });
    }
  }

  return {
    source: "alipay",
    filename,
    totalRows: parsed.data.length,
    skippedRows,
    failedRows: failedDetails.length,
    transactions,
    failedDetails,
  };
}

function buildTransaction(row: RawRow, source: "alipay"): ParsedTransaction {
  const dateStr = clean(row[COL.date]);
  const amountStr = clean(row[COL.amount]);
  const dirStr = clean(row[COL.direction]);
  const orderId = clean(row[COL.orderId]);

  if (!dateStr) throw new Error("缺少交易时间");
  if (!amountStr) throw new Error("缺少金额");
  if (!orderId) throw new Error("缺少交易订单号");

  const amount = Number.parseFloat(amountStr);
  if (Number.isNaN(amount)) throw new Error(`金额无法解析: ${amountStr}`);

  const date = parseBeijingDate(dateStr);
  if (!date) throw new Error(`日期无法解析: ${dateStr}`);

  return {
    source,
    orderId,
    transactionDate: date.toISOString(),
    amount: Math.abs(amount),
    direction: dirStr === "收入" ? "income" : "expense",
    merchant: clean(row[COL.merchant]) || null,
    description: clean(row[COL.description]) || null,
    rawData: row,
  };
}

function clean(v: unknown): string {
  return String(v ?? "").replace(/[\t\s]+$/g, "").trim();
}

// 解析 "2026-04-05 12:34:56" 为 UTC（输入是北京时间）
function parseBeijingDate(s: string): Date | null {
  const m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})[\sT](\d{1,2}):(\d{1,2}):(\d{1,2})$/);
  if (!m) return null;
  const [, y, mo, d, h, mi, se] = m;
  // 北京时间 → UTC：减 8 小时
  const utcMs = Date.UTC(+y, +mo - 1, +d, +h, +mi, +se) - BEIJING_OFFSET_MS;
  return new Date(utcMs);
}

function emptyResult(filename: string, reason: string): ParseResult {
  return {
    source: "alipay",
    filename,
    totalRows: 0,
    skippedRows: 0,
    failedRows: 1,
    transactions: [],
    failedDetails: [{ row: 0, reason }],
  };
}
