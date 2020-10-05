create database if not exists inmobiliaria;
use inmobiliaria;

create table usuarios_inmobiliaria
(
    id integer unsigned not null primary key auto_increment,
    nombre varchar(50),
    usuario varchar(50),
    email varchar(50),
    clave varchar(50),
    activo tinyint(1) default 1

);


create table comerciales_inmobiliaria
(
    id integer unsigned not null primary key auto_increment,
    nombre varchar(50),
    usuario varchar(20),
    email varchar(50),
    clave varchar(50),
    apellidos varchar(50),
    imagen_perfil varchar(300),
    telefono varchar(50),
    activo tinyint(1) default 1

);

create table viviendas_inmobiliaria
(
    id integer unsigned not null primary key auto_increment,
    calle varchar(50),
    piso varchar(50),
    codigopostal varchar(50),
    localidad varchar(50),
    provincia varchar(50),
    pais varchar(50),
    activo tinyint(1) default 1


);


INSERT INTO usuarios_inmobiliaria(nombre, usuario, email, clave)
VALUES
("elena user", "elenhedz", "h@h.com", "123"),
("sonia user", "soniause", "a@a.com", "123"),
("antonio user", "antonuse", "c@c.com", "123"),
("maria user", "mariause", "b@b.com", "123"),
("cristina user", "crisuse", "t@t.com", "123")
;


INSERT INTO comerciales_inmobiliaria(nombre, apellidos, usuario, email, clave, telefono, imagen_perfil)
VALUES
("elena comer", "her ape", "elenacomer", "h@h.com", "1234", "971", "https://avatars.dicebear.com/api/initials/EC.svg"),
("sonia comer", "son ape", "soniacomer", "a@a.com", "1234", "971", "https://avatars.dicebear.com/api/initials/SC.svg"),
("antonio comer", "ant ape", "antoncomer", "c@c.com", "1234", "971", "https://avatars.dicebear.com/api/initials/AC.svg"),
("maria comer", "mar ape", "mariacomer", "b@b.com", "1234", "971", "https://avatars.dicebear.com/api/initials/MC.svg"),
("cristina comer", "cris ape", "criscomer", "t@t.com", "1234", "971", "https://avatars.dicebear.com/api/initials/CC.svg")
;


create table administradores
(
    id integer unsigned not null primary key auto_increment,
    usuario varchar(20),
    clave varchar(20),
    nombre varchar(50),
    apellidos varchar(50),
    email varchar(60),
    id_roles integer unsigned not null,
    imagen_perfil varchar(300),
    telefono varchar(50),
    activo tinyint(1) default 1
)
;

create table roles
(
    id integer unsigned not null primary key auto_increment,
    descripcion_rol varchar(50),
    activo tinyint(1) default 1
)
;

insert into roles (descripcion_rol, activo)
values
("administrador", 1),
("operador", 1)
;

alter table administradores add constraint fk_id_rol foreign key (id_roles) references roles(id);

insert into administradores (usuario, clave, nombre, apellidos, email, id_roles, telefono, imagen_perfil)
values
("nieves", "nieves", "nieves bla bla", "apellidos", "test@test.com", 1, "971", "https://avatars2.githubusercontent.com/u/69692460?s=460&u=7e384317342468d80d27e54325eb5c79ada3c408&v=4")
;

