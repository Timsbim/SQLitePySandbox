CREATE TABLE "nucleotide-count" (
    strand TEXT CHECK (NOT "strand" GLOB '*[^ACGT]*'),
    result TEXT
);
INSERT INTO "nucleotide-count" (strand)
    VALUES
        (''), ('G'), ('GGGGGGG'),
        ('AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC');
