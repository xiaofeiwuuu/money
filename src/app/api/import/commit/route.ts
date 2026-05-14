import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/db";
import type { CommitResult } from "@/lib/types";

export const runtime = "nodejs";

const TxSchema = z.object({
  source: z.enum(["alipay", "wechat"]),
  orderId: z.string().min(1),
  transactionDate: z.string(),
  amount: z.number(),
  direction: z.enum(["income", "expense"]),
  merchant: z.string().nullable(),
  description: z.string().nullable(),
  rawData: z.unknown(),
});

const BodySchema = z.object({
  filename: z.string(),
  source: z.enum(["alipay", "wechat"]),
  totalRows: z.number(),
  failedRows: z.number(),
  transactions: z.array(TxSchema),
});

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const data = BodySchema.parse(body);

    // 批量插入：使用 createMany + skipDuplicates 依靠 (source, orderId) 唯一索引去重
    const result = await prisma.transaction.createMany({
      data: data.transactions.map((t) => ({
        source: t.source,
        orderId: t.orderId,
        transactionDate: new Date(t.transactionDate),
        amount: t.amount,
        direction: t.direction,
        merchant: t.merchant,
        description: t.description,
        rawData: t.rawData as object,
      })),
      skipDuplicates: true,
    });

    const inserted = result.count;
    const skipped = data.transactions.length - inserted;

    const session = await prisma.importSession.create({
      data: {
        source: data.source,
        filename: data.filename,
        totalRows: data.totalRows,
        insertedRows: inserted,
        skippedRows: skipped,
        failedRows: data.failedRows,
      },
    });

    const response: CommitResult = {
      inserted,
      skipped,
      failed: data.failedRows,
      sessionId: session.id,
    };
    return NextResponse.json(response);
  } catch (e) {
    console.error("[commit] error:", e);
    const msg = e instanceof Error ? e.message : "导入失败";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
