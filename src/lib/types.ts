// 共享类型

export type Source = "alipay" | "wechat";

export type Direction = "income" | "expense";

// 解析后的单条交易（待写入数据库）
export interface ParsedTransaction {
  source: Source;
  orderId: string;
  transactionDate: string; // ISO 字符串
  amount: number;
  direction: Direction;
  merchant: string | null;
  description: string | null;
  rawData: Record<string, unknown>;
}

// /api/import/parse 返回
export interface ParseResult {
  source: Source;
  filename: string;
  totalRows: number;
  skippedRows: number; // 头部说明行 + 中性交易等
  failedRows: number;
  transactions: ParsedTransaction[];
  failedDetails: Array<{ row: number; reason: string; data?: unknown }>;
}

// /api/import/commit 返回
export interface CommitResult {
  inserted: number;
  skipped: number; // 已存在的（去重跳过）
  failed: number;
  sessionId: string;
}

// 列表查询参数
export interface ListQuery {
  page?: number;
  pageSize?: number;
  dateFrom?: string;
  dateTo?: string;
  direction?: Direction;
  source?: Source;
  keyword?: string;
}

// 月度聚合返回
export interface MonthlyAggregate {
  month: string; // "2026-04"
  income: number;
  expense: number;
}
