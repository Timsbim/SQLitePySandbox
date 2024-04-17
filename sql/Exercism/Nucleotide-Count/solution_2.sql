WITH RECURSIVE counts(strand, pos, n, jstr) AS (
    SELECT strand, 2,
           format('$.%s', substr(strand, 1, 1)),
           json('{"A":0,"C":0,"G":0,"T":0}')
    FROM "nucleotide-count"
    UNION ALL
    SELECT strand, pos + 1,
           format('$.%s', substr(strand, pos, 1)),
           json_set(jstr, n, (jstr ->> n) + 1)
    FROM counts
    WHERE pos <= length(strand) + 1
)
UPDATE "nucleotide-count"
SET result = jstr
FROM counts
WHERE "nucleotide-count".strand = counts.strand
      AND pos = length(counts.strand) + 2;
