-- قاعدة بيانات نواة (SQL). تُنفَّذ على SQLite:  sqlite3 nawah.db < nawah_database.sql
BEGIN TRANSACTION;
CREATE TABLE analyses (
	id INTEGER NOT NULL, 
	image_path VARCHAR, 
	ai_variety VARCHAR, 
	ai_confidence FLOAT, 
	variety_id INTEGER, 
	user_confirmed BOOLEAN, 
	corrected_variety VARCHAR, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(variety_id) REFERENCES varieties (id)
);
CREATE TABLE companies (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	name_en VARCHAR, 
	description TEXT, 
	country VARCHAR, 
	city VARCHAR, 
	founded_year INTEGER, 
	varieties VARCHAR, 
	website VARCHAR, 
	phone VARCHAR, 
	rating FLOAT, 
	featured BOOLEAN, 
	PRIMARY KEY (id)
);
INSERT INTO "companies" VALUES(1,'الفوعة','Al Foah','شركة التمور الوطنية في الإمارات، إحدى علامات مجموعة أغذية. تصدّر لأكثر من 45 دولة وتدعم أكثر من 20 ألف مزارع.','الإمارات','العين',2005,'','https://www.agthia.com/brands/al-foah/','',NULL,1);
INSERT INTO "companies" VALUES(2,'باتيل','Bateel','علامة تمور فاخرة، افتُتح أول بوتيك لها في الرياض عام 1991.','السعودية','الرياض',NULL,'','https://www.bateel.com/','',NULL,1);
INSERT INTO "companies" VALUES(3,'تمارنا','Temarna','مصنع لتعبئة التمور في الأحساء.','السعودية','الأحساء',NULL,'','https://www.temarna.com/','',NULL,0);
INSERT INTO "companies" VALUES(4,'مصنع تمور القصيم',NULL,'مصنع لتعبئة التمور في البدائع بمنطقة القصيم.','السعودية','البدائع',NULL,'','','',NULL,0);
INSERT INTO "companies" VALUES(5,'باسقات القصيم',NULL,'مصنع لتعبئة التمور في بريدة.','السعودية','بريدة',NULL,'','','',NULL,0);
INSERT INTO "companies" VALUES(6,'الإمتياز لمعالجة وتصنيع التمور',NULL,'مصنع لمعالجة التمور وتصنيعها في بريدة.','السعودية','بريدة',NULL,'','','',NULL,0);
INSERT INTO "companies" VALUES(7,'تمارا',NULL,'مصنع لتعبئة التمور في الرياض.','السعودية','الرياض',NULL,'','','',NULL,0);
INSERT INTO "companies" VALUES(8,'تمور العثمانية',NULL,'مصنع لتعبئة التمور في الرياض.','السعودية','الرياض',NULL,'','','',NULL,0);
INSERT INTO "companies" VALUES(9,'أحد',NULL,'مصنع لتعبئة التمور في المنطقة الصناعية بالمدينة المنورة.','السعودية','المدينة المنورة',NULL,'','','',NULL,0);
INSERT INTO "companies" VALUES(10,'الجزيرة',NULL,'مصنع لتعبئة التمور في الأحساء.','السعودية','الأحساء',NULL,'','','',NULL,0);
INSERT INTO "companies" VALUES(11,'مواسم',NULL,'مصنع لتعبئة التمور في المبرز بالأحساء.','السعودية','المبرز',NULL,'','','',NULL,0);
INSERT INTO "companies" VALUES(12,'تيماء',NULL,'مصنع لتعبئة التمور في تيماء.','السعودية','تيماء',NULL,'','','',NULL,0);
CREATE TABLE suggestions (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	country VARCHAR, 
	city VARCHAR, 
	website VARCHAR, 
	phone VARCHAR, 
	status VARCHAR, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE varieties (
	id INTEGER NOT NULL, 
	name_ar VARCHAR NOT NULL, 
	name_en VARCHAR, 
	calories_per_100g FLOAT, 
	sugar_per_100g FLOAT, 
	calories_per_date FLOAT, 
	description TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (name_ar)
);
INSERT INTO "varieties" VALUES(1,'سكري','Sukkari',300.0,70.0,24.0,'تمر ذهبي ناعم شديد الحلاوة، من أشهر أنواع القصيم.');
INSERT INTO "varieties" VALUES(2,'عجوة','Ajwa',277.0,66.0,20.0,'تمر أسود مائل للبني من المدينة المنورة، طري ومعتدل الحلاوة.');
INSERT INTO "varieties" VALUES(3,'خلاص','Khalas',290.0,68.0,23.0,'تمر بني ذهبي من الأحساء، طعمه يشبه الكراميل.');
INSERT INTO "varieties" VALUES(4,'صقعي','Segai',282.0,64.0,22.0,'تمر ملون بين الأصفر والأحمر، قوامه شبه جاف.');
INSERT INTO "varieties" VALUES(5,'مجدول','Medjool',277.0,66.0,66.0,'تمر كبير الحجم لحمي وطري، يسمى ملك التمور.');
INSERT INTO "varieties" VALUES(6,'صفاوي','Safawi',285.0,65.0,21.0,'تمر أسود لامع من المدينة، لحمه طري وحلاوته معتدلة.');
INSERT INTO "varieties" VALUES(7,'برحي','Barhi',280.0,63.0,22.0,'يؤكل طازجاً (خلال) أو رطباً، حلو جداً وهش.');
INSERT INTO "varieties" VALUES(8,'مبروم','Mabroom',285.0,65.0,25.0,'تمر طويل رفيع بني، من المدينة المنورة.');
COMMIT;
