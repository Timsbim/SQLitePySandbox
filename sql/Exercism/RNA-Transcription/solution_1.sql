UPDATE "rna-transcription"
SET result = replace(replace(replace(replace(replace(dna, 'A', 'U'), 'T', 'A'), 'G', 'X'), 'C', 'G'), 'X', 'C')
