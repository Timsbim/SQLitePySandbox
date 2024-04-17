WITH RECURSIVE counts(strand, pos, n, A, C, G, T) AS (
    SELECT strand, 2, substr(strand, 1, 1), 0, 0, 0, 0 FROM "nucleotide-count"
    UNION ALL
    SELECT strand, pos + 1, substr(strand, pos, 1),
           iif(n = 'A', A + 1, A), iif(n = 'C', C + 1, C),
           iif(n = 'G', G + 1, G), iif(n = 'T', T + 1, T)
    FROM counts
    WHERE pos <= length(strand) + 1
)
UPDATE "nucleotide-count"
SET result = format('{"A":%i,"C":%i,"G":%i,"T":%i}', A, C, G, T)
FROM counts
WHERE "nucleotide-count".strand = counts.strand
      AND pos = length(counts.strand) + 2;
