UPDATE gigasecond
SET result = strftime('%Y-%m-%dT%H:%M:%S', moment, '1000000000 seconds');
--SET result = strftime('%FT%T', moment, '1000000000 seconds');
