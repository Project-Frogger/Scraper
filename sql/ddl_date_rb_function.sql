"""
Принимает день и месяц проведения мероприятия,
возвращает дату проведения (типа данных date)
"""

CREATE DEFINER=`ufaile8o_parser`@`%` FUNCTION `ufaile8o_parser`.`date_rb_function`(`_day` int,`_month` text) RETURNS date
BEGIN
	DECLARE _eng varchar(50);
	DECLARE _rus varchar(50);
	DECLARE `_year` int;
	DECLARE `_date` date;
	DECLARE done INT DEFAULT FALSE;
	DECLARE cur CURSOR FOR SELECT eng, rus from `month`;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
	open cur;
	the_loop: LOOP

	-- get the values of each column into our variables
	FETCH cur INTO _eng,_rus;
	IF done THEN
	  LEAVE the_loop;
	END IF;
	set `_month`=replace(`_month`,_rus,_eng);
	END LOOP the_loop;

	set `_year` = IF(month(CURDATE()) > month(str_to_date(`_month`,'%M')), year(CURDATE()) + 1, year(CURDATE()));
	set `_date` = str_to_date(CONCAT(CONVERT(`_day`,char), ' ', `_month`, ' ', CONVERT(`_year`,char)),'%d %M %Y');

	CLOSE cur;
	return `_date`;
END
