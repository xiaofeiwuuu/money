import { NextRequest, NextResponse } from "next/server";
import { parseFile } from "@/lib/parsers";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("file");

    if (!file || !(file instanceof File)) {
      return NextResponse.json({ error: "缺少文件" }, { status: 400 });
    }

    if (file.size > 10 * 1024 * 1024) {
      return NextResponse.json({ error: "文件超过 10MB 限制" }, { status: 400 });
    }

    const result = await parseFile(file);
    return NextResponse.json(result);
  } catch (e) {
    console.error("[parse] error:", e);
    const msg = e instanceof Error ? e.message : "解析失败";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
