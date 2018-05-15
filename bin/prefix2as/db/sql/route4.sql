CREATE TABLE route4(
	id bigint auto_increment primary key,
	history_id integer,
	date bigint unsigned,
	asnum bigint unsigned,
	prefix varchar(18),
	start_ip bigint unsigned,
	end_ip bigint unsigned,
	size integer unsigned
);
