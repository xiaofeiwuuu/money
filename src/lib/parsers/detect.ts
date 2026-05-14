import type { Source } from "../types";

// 根据文件名 + 文件内容前几行判断来源
export function detectSource(filename: string, sample: string): Source | null {
  const name = filename.toLowerCase();
  const head = sample.slice(0, 2000);

  const isAlipay =
    name.includes("支付宝") ||
    name.includes("alipay") ||
    head.includes("支付宝账户") ||
    head.includes("支付宝支付科技");

  const isWechat =
    name.includes("微信") ||
    name.includes("wechat") ||
    head.includes("微信支付账单") ||
    head.includes("微信昵称");

  if (isAlipay && !isWechat) return "alipay";
  if (isWechat && !isAlipay) return "wechat";
  return null;
}
