"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { CheckCircle2, FileSpreadsheet, Loader2, Upload, XCircle } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import type { CommitResult, ParseResult } from "@/lib/types";

type Stage = "upload" | "parsing" | "preview" | "committing" | "done";

const SOURCE_LABEL = { alipay: "支付宝", wechat: "微信" } as const;
const DIRECTION_LABEL = { income: "收入", expense: "支出" } as const;

export default function ImportPage() {
  const router = useRouter();
  const [stage, setStage] = useState<Stage>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [commitResult, setCommitResult] = useState<CommitResult | null>(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel": [".xls"],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    disabled: stage !== "upload",
    onDrop: async (acceptedFiles, rejections) => {
      if (rejections.length > 0) {
        toast.error(rejections[0].errors[0]?.message || "文件不支持");
        return;
      }
      const f = acceptedFiles[0];
      if (!f) return;
      setFile(f);
      await handleParse(f);
    },
  });

  async function handleParse(f: File) {
    setStage("parsing");
    try {
      const fd = new FormData();
      fd.append("file", f);
      const res = await fetch("/api/import/parse", { method: "POST", body: fd });
      if (!res.ok) {
        const err = (await res.json()) as { error?: string };
        throw new Error(err.error || "解析失败");
      }
      const data = (await res.json()) as ParseResult;
      setParseResult(data);
      setStage("preview");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "解析失败");
      setStage("upload");
    }
  }

  async function handleCommit() {
    if (!parseResult) return;
    setStage("committing");
    try {
      const res = await fetch("/api/import/commit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: parseResult.filename,
          source: parseResult.source,
          totalRows: parseResult.totalRows,
          failedRows: parseResult.failedRows,
          transactions: parseResult.transactions,
        }),
      });
      if (!res.ok) {
        const err = (await res.json()) as { error?: string };
        throw new Error(err.error || "导入失败");
      }
      const data = (await res.json()) as CommitResult;
      setCommitResult(data);
      setStage("done");
      toast.success(`成功导入 ${data.inserted} 条，跳过 ${data.skipped} 条`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "导入失败");
      setStage("preview");
    }
  }

  function reset() {
    setStage("upload");
    setFile(null);
    setParseResult(null);
    setCommitResult(null);
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">导入账单</h1>
        <p className="text-sm text-muted-foreground mt-1">
          支持支付宝/微信导出的 CSV / XLSX 账单文件
        </p>
      </div>

      {stage === "upload" && (
        <div
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors",
            isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-muted-foreground/50"
          )}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-lg font-medium">
            {isDragActive ? "松开以上传" : "拖拽文件到这里，或点击选择"}
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            支持 .csv .xlsx .xls · 单文件不超过 10MB
          </p>
        </div>
      )}

      {stage === "parsing" && (
        <Card>
          <CardContent className="flex items-center gap-4 p-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            <div>
              <p className="font-medium">正在解析...</p>
              <p className="text-sm text-muted-foreground">{file?.name}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {stage === "preview" && parseResult && (
        <PreviewView
          parseResult={parseResult}
          onConfirm={handleCommit}
          onCancel={reset}
        />
      )}

      {stage === "committing" && (
        <Card>
          <CardContent className="flex items-center gap-4 p-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            <p className="font-medium">正在写入数据库...</p>
          </CardContent>
        </Card>
      )}

      {stage === "done" && commitResult && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <CardTitle>导入完成</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <Stat label="新增" value={commitResult.inserted} tone="green" />
              <Stat label="已存在（跳过）" value={commitResult.skipped} tone="zinc" />
              <Stat label="失败" value={commitResult.failed} tone={commitResult.failed > 0 ? "red" : "zinc"} />
            </div>
            <Separator />
            <div className="flex gap-2">
              <Button onClick={() => router.push("/transactions")}>查看交易列表</Button>
              <Button variant="outline" onClick={reset}>继续导入</Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function PreviewView({
  parseResult,
  onConfirm,
  onCancel,
}: {
  parseResult: ParseResult;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  const { source, filename, totalRows, skippedRows, failedRows, transactions, failedDetails } = parseResult;
  const previewRows = transactions.slice(0, 100);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5 text-muted-foreground" />
              <CardTitle className="text-base">{filename}</CardTitle>
              <Badge variant="secondary">{SOURCE_LABEL[source]}</Badge>
            </div>
          </div>
          <CardDescription>请确认解析结果。点击下方"导入"将写入数据库（已存在的订单号会自动跳过）。</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <Stat label="原始行数" value={totalRows} tone="zinc" />
            <Stat label="可导入" value={transactions.length} tone="green" />
            <Stat label="跳过（非收/支）" value={skippedRows} tone="zinc" />
            <Stat label="失败" value={failedRows} tone={failedRows > 0 ? "red" : "zinc"} />
          </div>
        </CardContent>
      </Card>

      {failedRows > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-600" />
              <CardTitle className="text-base">解析失败 ({failedRows} 行)</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="text-sm space-y-1">
              {failedDetails.slice(0, 10).map((f, i) => (
                <li key={i} className="text-muted-foreground">
                  第 {f.row} 行：{f.reason}
                </li>
              ))}
              {failedDetails.length > 10 && (
                <li className="text-muted-foreground">...还有 {failedDetails.length - 10} 行</li>
              )}
            </ul>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">数据预览（前 {previewRows.length} 条）</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="max-h-[500px] overflow-auto">
            <Table>
              <TableHeader className="sticky top-0 bg-background">
                <TableRow>
                  <TableHead>时间</TableHead>
                  <TableHead>方向</TableHead>
                  <TableHead className="text-right">金额</TableHead>
                  <TableHead>商家</TableHead>
                  <TableHead>说明</TableHead>
                  <TableHead className="font-mono text-xs">订单号</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {previewRows.map((t, i) => (
                  <TableRow key={i}>
                    <TableCell className="whitespace-nowrap text-sm">
                      {formatDate(t.transactionDate)}
                    </TableCell>
                    <TableCell>
                      <Badge variant={t.direction === "income" ? "default" : "secondary"}>
                        {DIRECTION_LABEL[t.direction]}
                      </Badge>
                    </TableCell>
                    <TableCell className={cn("text-right font-mono",
                      t.direction === "income" ? "text-green-600" : "text-red-600"
                    )}>
                      {t.direction === "income" ? "+" : "-"}
                      {t.amount.toFixed(2)}
                    </TableCell>
                    <TableCell className="max-w-[160px] truncate">{t.merchant || "—"}</TableCell>
                    <TableCell className="max-w-[260px] truncate text-muted-foreground">{t.description || "—"}</TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground">{t.orderId}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-2 justify-end">
        <Button variant="outline" onClick={onCancel}>取消</Button>
        <Button onClick={onConfirm} disabled={transactions.length === 0}>
          导入 {transactions.length} 条
        </Button>
      </div>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: number; tone: "green" | "red" | "zinc" }) {
  const toneClasses = {
    green: "text-green-600",
    red: "text-red-600",
    zinc: "text-foreground",
  };
  return (
    <div>
      <div className="text-sm text-muted-foreground">{label}</div>
      <div className={cn("text-2xl font-semibold mt-1", toneClasses[tone])}>{value}</div>
    </div>
  );
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => n.toString().padStart(2, "0");
  // 显示为北京时间
  const beijing = new Date(d.getTime() + 8 * 60 * 60 * 1000);
  return `${beijing.getUTCFullYear()}-${pad(beijing.getUTCMonth() + 1)}-${pad(beijing.getUTCDate())} ${pad(beijing.getUTCHours())}:${pad(beijing.getUTCMinutes())}`;
}
