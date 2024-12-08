SET search_path TO SIJARTA, public;

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

-- Trigger 2
CREATE OR REPLACE FUNCTION refund_mypay_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_nominal DECIMAL;
    v_user_id UUID;
    v_status VARCHAR(50);
BEGIN
    SELECT TotalBiaya, IdPelanggan, sp.Status
    INTO v_nominal, v_user_id, v_status
    FROM TR_PEMESANAN_JASA tpj
    JOIN TR_PEMESANAN_STATUS tps ON tpj.Id = tps.IdTrPemesanan
    JOIN STATUS_PESANAN sp ON tps.IdStatus = sp.Id
    WHERE tpj.Id = NEW.IdTrPemesanan
    ORDER BY tps.TglWaktu DESC
    LIMIT 1;

    IF NEW.IdStatus = (SELECT Id FROM STATUS_PESANAN WHERE Status = 'Dibatalkan') THEN
        IF v_status = 'Mencari Pekerja' THEN
            UPDATE PENGGUNA
            SET SaldoMyPay = SaldoMyPay + v_nominal
            WHERE Id = v_user_id;
        ELSE
            RAISE EXCEPTION 'Pesanan tidak dapat dibatalkan. Status saat ini adalah %', v_status;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_status_update
BEFORE INSERT ON TR_PEMESANAN_STATUS
FOR EACH ROW EXECUTE FUNCTION refund_mypay_trigger();

-- Trigger 3
CREATE OR REPLACE FUNCTION validate_voucher_usage(
    id_diskon VARCHAR,
    transaksi_nominal DECIMAL,
    id_pelanggan uuid
) RETURNS VOID AS $$
DECLARE
    kuota_penggunaan INT;
    jml_hari_berlaku INT;
    tgl_awal_voucher DATE;
    tgl_akhir_promo DATE;
    min_transaksi INT;
    is_voucher BOOLEAN;
    is_promo BOOLEAN;
BEGIN
    -- Cek apakah id_diskon merupakan voucher
    SELECT COUNT(*) > 0
    INTO is_voucher
    FROM VOUCHER
    WHERE Kode = id_diskon;

    -- Cek apakah id_diskon merupakan promo
    SELECT COUNT(*) > 0
    INTO is_promo
    FROM PROMO
    WHERE Kode = id_diskon;

    -- Jika voucher, cek kuota penggunaan dan batas hari berlaku
    IF is_voucher THEN
        SELECT KuotaPenggunaan, JmlHariBerlaku
        INTO kuota_penggunaan, jml_hari_berlaku
        FROM VOUCHER
        WHERE Kode = id_diskon;
        
        SELECT tglawal INTO tgl_awal_voucher
        FROM TR_PEMBELIAN_VOUCHER
        WHERE IdVoucher = id_diskon AND IdPelanggan = id_pelanggan;

        -- Cek kuota penggunaan
        IF kuota_penggunaan <= 0 THEN
            RAISE EXCEPTION 'Voucher telah habis kuota penggunaan.';
        END IF;

        -- Cek batas hari berlaku
        IF NOW()::DATE > (tgl_awal_voucher + jml_hari_berlaku) THEN
            RAISE EXCEPTION 'Voucher telah melewati batas hari berlaku.';
        END IF;
    END IF;

    -- Jika promo, cek batas hari berlaku
    IF is_promo THEN
        SELECT TglAkhirBerlaku
        INTO tgl_akhir_promo
        FROM PROMO
        WHERE Kode = id_diskon;

        IF NOW()::DATE > tgl_akhir_promo THEN
            RAISE EXCEPTION 'Promo telah melewati batas hari berlaku.';
        END IF;
    END IF;

    -- Cek minimal transaksi untuk diskon
    SELECT MinTrPemesanan
    INTO min_transaksi
    FROM DISKON
    WHERE Kode = id_diskon;

    IF transaksi_nominal < min_transaksi THEN
        RAISE EXCEPTION 'Nominal transaksi tidak memenuhi syarat minimal untuk diskon.';
    END IF;

END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION validate_voucher_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Panggil fungsi validasi hanya jika IdDiskon tidak null
    IF NEW.IdDiskon IS NOT NULL THEN
        PERFORM validate_voucher_usage(NEW.IdDiskon, NEW.TotalBiaya, NEW.IdPelanggan);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Buat trigger untuk pemesanan jasa
CREATE TRIGGER validate_voucher_before_insert
BEFORE INSERT ON TR_PEMESANAN_JASA
FOR EACH ROW
EXECUTE FUNCTION validate_voucher_trigger();

-- Trigger 4
CREATE OR REPLACE FUNCTION pengiriman_nominal_jasa()
RETURNS TRIGGER AS $$
BEGIN
IF (NEW.IdStatus = (SELECT Id FROM STATUS_PESANAN WHERE Status = 'Selesai')) THEN
INSERT INTO TR_MYPAY
VALUES (uuid_generate_v4(), (SELECT IdPekerja FROM TR_PEMESANAN_JASA WHERE Id = NEW.IdTrPemesanan), CURRENT_DATE, (SELECT TotalBiaya FROM TR_PEMESANAN_JASA WHERE Id = NEW.IdTrPemesanan), (SELECT Id FROM KATEGORI_TR_MYPAY WHERE Nama ='Menerima honor transaksi jasa'));
UPDATE PENGGUNA
SET SaldoMyPay = SaldoMyPay + (SELECT TotalBiaya FROM TR_PEMESANAN_JASA WHERE Id = NEW.IdTrPemesanan)
WHERE Pengguna.Id = (SELECT IdPekerja FROM TR_PEMESANAN_JASA WHERE Id = NEW.IdTrPemesanan);
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER add_balance_pekerja
BEFORE INSERT ON TR_PEMESANAN_STATUS
FOR EACH ROW EXECUTE FUNCTION pengiriman_nominal_jasa();
-- status pesanan berubah melalui insert riwayat statusnya
