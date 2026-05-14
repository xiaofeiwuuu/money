import iconv from "iconv-lite";
import type { ParseResult } from "../types";
import { detectSource } from "./detect";
import { parseAlipay } from "./alipay";
import { parseWechatCSV, parseWechatXLSX } from "./wechat";

// 入口：根据文件类型 + 来源选择解析器
export async function parseFile(file: File): Promise<ParseResult> {
  const filename = file.name;
  const buffer = await file.arrayBuffer();
  const ext = filename.toLowerCase().split(".").pop() || "";

  if (ext === "xlsx" || ext === "xls") {
    // XLSX 目前只支持微信
    return parseWechatXLSX(buffer, filename);
  }

  // CSV 文件：先尝试 UTF-8 解码，若无法识别 marker 则用 GBK
  const text = decodeText(buffer);
  const source = detectSource(filename, text);

  if (source === "alipay") return parseAlipay(text, filename);
  if (source === "wechat") return parseWechatCSV(text, filename);

  return {
    source: "alipay",
    filename,
    totalRows: 0,
    skippedRows: 0,
    failedRows: 1,
    transactions: [],
    failedDetails: [{ row: 0, reason: "无法识别账单来源（请确认是支付宝或微信账单）" }],
  };
}

function decodeText(buffer: ArrayBuffer): string {
  const bytes = Buffer.from(buffer);
  // 先用 UTF-8 解码
  const utf8 = bytes.toString("utf-8");
  if (utf8.includes("交易时间") || utf8.includes("微信支付")) {
    // 移除 BOM
    return utf8.replace(/^﻿/, "");
  }
  // 退回 GBK（支付宝原始 CSV）
  return iconv.decode(bytes, "gbk");
}
