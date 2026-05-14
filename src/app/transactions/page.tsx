"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2, Search, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

const SOURCE_LABEL = { alipay: "支付宝", wechat: "微信" } as const;
const DIRECTION_LABEL = { income: "收入", expense: "支出" } as const;

interface Transaction {
  id: string;
  source: "alipay" | "wechat";
  orderId: string;
  transactionDate: string;
  amount: number;
  direction: "income" | "expense";
  merchant: string | null;
  description: string | null;
}

interface Filters {
  dateFrom: string;
  dateTo: string;
  direction: string;
  source: string;
  keyword: string;
}

const PAGE_SIZE = 50;

export default function TransactionsPage() {
  const [items, setItems] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    dateFrom: "",
    dateTo: "",
    direction: "all",
    source: "all",
    keyword: "",
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("pageSize", String(PAGE_SIZE));
      if (filters.dateFrom) params.set("dateFrom", filters.dateFrom);
      if (filters.dateTo) params.set("dateTo", filters.dateTo);
      if (filters.direction !== "all") params.set("direction", filters.direction);
      if (filters.source !== "all") params.set("source", filters.source);
      if (filters.keyword) params.set("keyword", filters.keyword);

      const res = await fetch(`/api/transactions?${params}`);
      const data = await res.json();
      setItems(data.items);
      setTotal(data.total);
    } catch (e) {
      toast.error("加载失败");
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  async function handleDelete(id: string) {
    if (!confirm("确认删除这条交易？")) return;
    const res = await fetch("/api/transactions", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ids: [id] }),
    });
    if (res.ok) {
      toast.success("已删除");
      fetchData();
    } else {
      toast.error("删除失败");
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold">交易记录</h1>
          <p className="text-sm text-muted-foreground mt-1">共 {total} 条</p>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="dateFrom">起始日期</Label>
              <Input
                id="dateFrom"
                type="date"
                value={filters.dateFrom}
                onChange={(e) => {
                  setFilters((f) => ({ ...f, dateFrom: e.target.value }));
                  setPage(1);
                }}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="dateTo">结束日期</Label>
              <Input
                id="dateTo"
                type="date"
                value={filters.dateTo}
                onChange={(e) => {
                  setFilters((f) => ({ ...f, dateTo: e.target.value }));
                  setPage(1);
                }}
              />
            </div>
            <div className="space-y-1.5">
              <Label>方向</Label>
              <Select
                value={filters.direction}
                onValueChange={(v) => {
                  setFilters((f) => ({ ...f, direction: v }));
                  setPage(1);
                }}
              >
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部</SelectItem>
                  <SelectItem value="income">收入</SelectItem>
                  <SelectItem value="expense">支出</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>来源</Label>
              <Select
                value={filters.source}
                onValueChange={(v) => {
                  setFilters((f) => ({ ...f, source: v }));
                  setPage(1);
                }}
              >
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部</SelectItem>
                  <SelectItem value="alipay">支付宝</SelectItem>
                  <SelectItem value="wechat">微信</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="keyword">关键字</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="keyword"
                  placeholder="商家/说明"
                  className="pl-8"
                  value={filters.keyword}
                  onChange={(e) => {
                    setFilters((f) => ({ ...f, keyword: e.target.value }));
                    setPage(1);
                  }}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : items.length === 0 ? (
            <div className="text-center py-16 text-muted-foreground">暂无数据</div>
          ) : (
            <div className="overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="whitespace-nowrap">时间</TableHead>
                    <TableHead>方向</TableHead>
                    <TableHead className="text-right">金额</TableHead>
                    <TableHead>商家</TableHead>
                    <TableHead>说明</TableHead>
                    <TableHead>来源</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((t) => (
                    <TableRow key={t.id}>
                      <TableCell className="whitespace-nowrap text-sm">
                        {formatDate(t.transactionDate)}
                      </TableCell>
                      <TableCell>
                        <Badge variant={t.direction === "income" ? "default" : "secondary"}>
                          {DIRECTION_LABEL[t.direction]}
                        </Badge>
                      </TableCell>
                      <TableCell className={cn(
                        "text-right font-mono",
                        t.direction === "income" ? "text-green-600" : "text-red-600"
                      )}>
                        {t.direction === "income" ? "+" : "-"}
                        {t.amount.toFixed(2)}
                      </TableCell>
                      <TableCell className="max-w-[200px] truncate">{t.merchant || "—"}</TableCell>
                      <TableCell className="max-w-[280px] truncate text-muted-foreground">{t.description || "—"}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{SOURCE_LABEL[t.source]}</Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(t.id)}
                          aria-label="删除"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            上一页
          </Button>
          <span className="text-sm text-muted-foreground">
            第 {page} / {totalPages} 页
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            下一页
          </Button>
        </div>
      )}
    </div>
  );
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => n.toString().padStart(2, "0");
  const beijing = new Date(d.getTime() + 8 * 60 * 60 * 1000);
  return `${beijing.getUTCFullYear()}-${pad(beijing.getUTCMonth() + 1)}-${pad(beijing.getUTCDate())} ${pad(beijing.getUTCHours())}:${pad(beijing.getUTCMinutes())}`;
}
