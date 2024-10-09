WITH RECURSIVE comps(dna, comp, pos) AS (
    SELECT dna, "", 1 FROM "rna-transcription"
    UNION
    SELECT
        dna,
        comp || CASE substring(dna, pos, 1)
            WHEN "G" THEN "C"
            WHEN "C" THEN "G"
            WHEN "T" THEN "A"
            WHEN "A" THEN "U"
        END,
        pos + 1
    FROM comps
    WHERE pos <= length(dna) + 1
)
UPDATE "rna-transcription"
SET result = comp
FROM comps WHERE comps.dna = "rna-transcription".dna
