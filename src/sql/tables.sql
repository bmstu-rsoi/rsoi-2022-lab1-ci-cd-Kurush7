create table if not exists persons
(
    id      integer generated always as identity
        constraint authors_pkey primary key,
    age     integer,
    name    varchar(256),
    address varchar(256),
    work    varchar(256)
);