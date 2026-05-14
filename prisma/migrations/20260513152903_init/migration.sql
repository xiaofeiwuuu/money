-- CreateTable
CREATE TABLE "Transaction" (
    "id" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "orderId" TEXT NOT NULL,
    "transactionDate" TIMESTAMP(3) NOT NULL,
    "amount" DECIMAL(12,2) NOT NULL,
    "direction" TEXT NOT NULL,
    "merchant" TEXT,
    "description" TEXT,
    "rawData" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Transaction_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ImportSession" (
    "id" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "filename" TEXT NOT NULL,
    "totalRows" INTEGER NOT NULL,
    "insertedRows" INTEGER NOT NULL,
    "skippedRows" INTEGER NOT NULL,
    "failedRows" INTEGER NOT NULL,
    "errorDetails" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ImportSession_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Transaction_transactionDate_idx" ON "Transaction"("transactionDate");

-- CreateIndex
CREATE INDEX "Transaction_source_idx" ON "Transaction"("source");

-- CreateIndex
CREATE UNIQUE INDEX "Transaction_source_orderId_key" ON "Transaction"("source", "orderId");

-- CreateIndex
CREATE INDEX "ImportSession_createdAt_idx" ON "ImportSession"("createdAt");
