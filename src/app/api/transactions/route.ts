import { NextRequest, NextResponse } from "next/server";
import { Prisma } from "@/generated/prisma/client";
import { prisma } from "@/lib/db";

export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const page = Math.max(1, Number.parseInt(searchParams.get("page") || "1", 10));
  const pageSize = Math.min(100, Math.max(1, Number.parseInt(searchParams.get("pageSize") || "50", 10)));
  const dateFrom = searchParams.get("dateFrom");
  const dateTo = searchParams.get("dateTo");
  const direction = searchParams.get("direction");
  const source = searchParams.get("source");
  const keyword = (searchParams.get("keyword") || "").trim();

  const where: Prisma.TransactionWhereInput = {};
  if (dateFrom || dateTo) {
    where.transactionDate = {};
    if (dateFrom) where.transactionDate.gte = new Date(dateFrom);
    if (dateTo) where.transactionDate.lte = new Date(dateTo);
  }
  if (direction === "income" || direction === "expense") where.direction = direction;
  if (source === "alipay" || source === "wechat") where.source = source;
  if (keyword) {
    where.OR = [
      { merchant: { contains: keyword, mode: "insensitive" } },
      { description: { contains: keyword, mode: "insensitive" } },
    ];
  }

  const [total, items] = await Promise.all([
    prisma.transaction.count({ where }),
    prisma.transaction.findMany({
      where,
      orderBy: { transactionDate: "desc" },
      skip: (page - 1) * pageSize,
      take: pageSize,
    }),
  ]);

  return NextResponse.json({
    items: items.map((t) => ({
      ...t,
      amount: Number(t.amount),
      transactionDate: t.transactionDate.toISOString(),
      createdAt: t.createdAt.toISOString(),
      updatedAt: t.updatedAt.toISOString(),
    })),
    total,
    page,
    pageSize,
  });
}

export async function DELETE(req: NextRequest) {
  const body = (await req.json().catch(() => ({}))) as { ids?: string[] };
  if (!Array.isArray(body.ids) || body.ids.length === 0) {
    return NextResponse.json({ error: "缺少 ids" }, { status: 400 });
  }
  const result = await prisma.transaction.deleteMany({
    where: { id: { in: body.ids } },
  });
  return NextResponse.json({ deleted: result.count });
}
