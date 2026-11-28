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