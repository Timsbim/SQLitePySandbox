CREATE TABLE "nucleotide-count" (
    strand TEXT CHECK (NOT "strand" GLOB '*[^ACGT]*'),
    result TEXT
);
