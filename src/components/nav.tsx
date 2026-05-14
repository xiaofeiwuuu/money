"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, List, Upload, Wallet } from "lucide-react";
import { cn } from "@/lib/utils";

const items = [
  { href: "/import", label: "导入", icon: Upload },
  { href: "/transactions", label: "交易", icon: List },
  { href: "/analytics", label: "分析", icon: BarChart3 },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <header className="border-b bg-background">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 h-14">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <Wallet className="h-5 w-5" />
          <span>家庭账本</span>
        </Link>
        <nav className="flex items-center gap-1">
          {items.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors",
                  active
                    ? "bg-secondary text-secondary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
