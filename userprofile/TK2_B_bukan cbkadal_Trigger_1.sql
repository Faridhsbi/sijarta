-- 1
CREATE OR REPLACE FUNCTION cek_nomor_hp_terdaftar()
RETURNS TRIGGER AS 
$$
DECLARE
    nomor_terdaftar INTEGER;
BEGIN
    SELECT COUNT(*) INTO nomor_terdaftar
    FROM PENGGUNA
    WHERE NoHP = NEW.NoHP;

    IF nomor_terdaftar > 0 THEN
        RAISE EXCEPTION 'Nomor HP % sudah terdaftar', NEW.NoHP;
    END IF;
    RETURN NEW;
END;
$$
LANGUAGE PLPGSQL;

CREATE TRIGGER trigger_hp_pengguna
BEFORE INSERT ON PENGGUNA
FOR EACH ROW
EXECUTE PROCEDURE cek_nomor_hp_terdaftar();


-- 2
CREATE OR REPLACE FUNCTION cek_duplikasi_rekening()
RETURNS TRIGGER AS 
$$
DECLARE
    rekening_terdaftar INTEGER;
BEGIN
    SELECT COUNT(*) INTO rekening_terdaftar
    FROM PEKERJA
    WHERE NamaBank = NEW.NamaBank AND NomorRekening = NEW.NomorRekening;

    IF rekening_terdaftar > 0 THEN
        RAISE EXCEPTION 'Kombinasi NamaBank % dan NomorRekening % sudah terdaftar', NEW.NamaBank, NEW.NomorRekening;
    END IF;
    RETURN NEW;
END;
$$
LANGUAGE PLPGSQL;

CREATE TRIGGER trigger_insert_pekerja
BEFORE INSERT ON PEKERJA
FOR EACH ROW
EXECUTE PROCEDURE cek_duplikasi_rekening();

