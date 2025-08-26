CREATE TABLE say (
	number 			INTEGER NOT NULL,
	expected_result	TEXT,
  	expected_error 	TEXT,
	result 			TEXT,
  	error  			TEXT
);
INSERT INTO say (number, expected_result, expected_error) VALUES
	(0, 'zero', NULL),
    (1, 'one', NULL),
    (14, 'fourteen', NULL),
    (19, 'nineteen', NULL),
    (20, 'twenty', NULL),
    (22, 'twenty-two', NULL),
    (30, 'thirty', NULL),
    (99, 'ninety-nine', NULL),
    (100, 'one hundred', NULL),
    (123, 'one hundred twenty-three', NULL),
    (200, 'two hundred', NULL),
    (999, 'nine hundred ninety-nine', NULL),
    (1000, 'one thousand', NULL),
    (1234, 'one thousand two hundred thirty-four', NULL),
    (1000000, 'one million', NULL),
    (1002345, 'one million two thousand three hundred forty-five', NULL),
    (1000000000, 'one billion', NULL),
    (987654321123, 'nine hundred eighty-seven billion six hundred fifty-four million three hundred twenty-one thousand one hundred twenty-three', NULL),
    (-1, NULL, 'input out of range'),
    (1000000000000, NULL, 'input out of range');
