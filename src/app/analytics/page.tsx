"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { MonthlyAggregate } from "@/lib/types";

export default function AnalyticsPage() {
  const [data, setData] = useState<MonthlyAggregate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/analytics/monthly")
      .then((r) => r.json())
      .then((d: MonthlyAggregate[]) => setData(d))
      .finally(() => setLoading(false));
  }, []);

  const totalIncome = data.reduce((s, d) => s + d.income, 0);
  const totalExpense = data.reduce((s, d) => s + d.expense, 0);
  const balance = totalIncome - totalExpense;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">数据分析</h1>
        <p className="text-sm text-muted-foreground mt-1">最近 12 个月收支概览</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SummaryCard label="收入合计" value={totalIncome} tone="green" />
        <SummaryCard label="支出合计" value={totalExpense} tone="red" />
        <SummaryCard label="结余" value={balance} tone={balance >= 0 ? "green" : "red"} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>月度收支</CardTitle>
          <CardDescription>按交易时间所在月份聚合（北京时区）</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : data.length === 0 ? (
            <div className="flex items-center justify-center h-64 text-muted-foreground">
              暂无数据
            </div>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="month" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip
                    formatter={(v: number) => `¥${v.toFixed(2)}`}
                    contentStyle={{ background: "var(--background)", border: "1px solid var(--border)" }}
                  />
                  <Legend />
                  <Bar dataKey="income" name="收入" fill="#16a34a" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="expense" name="支出" fill="#dc2626" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "green" | "red";
}) {
  const color = tone === "green" ? "text-green-600" : "text-red-600";
  const sign = value >= 0 ? "" : "-";
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="text-sm text-muted-foreground">{label}</div>
        <div className={`text-2xl font-semibold mt-1 ${color}`}>
          {sign}¥{Math.abs(value).toFixed(2)}
        </div>
      </CardContent>
    </Card>
  );
}
