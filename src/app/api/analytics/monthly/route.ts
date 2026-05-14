import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import type { MonthlyAggregate } from "@/lib/types";

export const runtime = "nodejs";

// 最近 12 个月收支聚合（按北京时间月份分组）
export async function GET() {
  // 北京时区分组：date_trunc 在 'Asia/Shanghai' 时区
  const rows = await prisma.$queryRaw<
    Array<{ month: Date; direction: string; total: number }>
  >`
    SELECT
      date_trunc('month', "transactionDate" AT TIME ZONE 'Asia/Shanghai') AS month,
      "direction",
      SUM("amount")::float AS total
    FROM "Transaction"
    WHERE "transactionDate" >= (now() AT TIME ZONE 'Asia/Shanghai' - interval '12 months')
    GROUP BY 1, 2
    ORDER BY 1 ASC
  `;

  // 转成 { month, income, expense } 形式
  const map = new Map<string, MonthlyAggregate>();
  for (const r of rows) {
    const m = r.month.toISOString().slice(0, 7); // "2026-04"
    if (!map.has(m)) map.set(m, { month: m, income: 0, expense: 0 });
    const entry = map.get(m)!;
    if (r.direction === "income") entry.income = Number(r.total);
    else if (r.direction === "expense") entry.expense = Number(r.total);
  }

  return NextResponse.json(Array.from(map.values()));
}
