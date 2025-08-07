CREATE TABLE anagram (
    subject    TEXT NOT NULL,
    candidates TEXT NOT NULL,  -- json array of strings
    result     TEXT            -- json array of strings
);
