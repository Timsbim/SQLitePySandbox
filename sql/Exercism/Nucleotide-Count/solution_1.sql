WITH RECURSIVE counts(strand, pos, n) AS (
    SELECT strand, 1, json('{"A":0,"C":0,"G":0,"T":0}') FROM "nucleotide-count"
    UNION ALL
    SELECT
        strand,
        pos + 1,
        CASE substr(strand, pos, 1)
            WHEN 'A' THEN json_set(n, '$.A', (n ->> '$.A') + 1)
            WHEN 'C' THEN json_set(n, '$.C', (n ->> '$.C') + 1)
            WHEN 'G' THEN json_set(n, '$.G', (n ->> '$.G') + 1)
            ELSE json_set(n, '$.T', (n ->> '$.T') + 1)
        END
    FROM counts
    WHERE pos <= length(strand)
)
UPDATE "nucleotide-count"
SET result = n
FROM counts
WHERE "nucleotide-count".strand = counts.strand
      AND pos = length(counts.strand) + 1;
