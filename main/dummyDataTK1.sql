CREATE SCHEMA SIJARTA;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- biar bisa pakai fungsi uuid_generate_v4()
SET search_path TO SIJARTA;

-- tabel 1, USER gabisa udah reserved name di postgre
CREATE TABLE PENGGUNA (
	Id UUID,
	Nama VARCHAR,
	JenisKelamin CHAR(1) CHECK (JenisKelamin in ('L','P')),
	NoHP VARCHAR(15),
	Pwd VARCHAR,
	TglLahir DATE,
	Alamat VARCHAR,
	SaldoMyPay DECIMAL,

	PRIMARY KEY (Id)

);

-- tabel 2
CREATE TABLE PELANGGAN (
	Id UUID,
	Level VARCHAR,
  PRIMARY KEY (Id),
	FOREIGN KEY (Id) REFERENCES PENGGUNA(Id)
);

-- tabel 3
CREATE TABLE PEKERJA (
	Id UUID,
	NamaBank VARCHAR,
	NomorRekening VARCHAR(16),
	NPWP VARCHAR(16),
	LinkFoto VARCHAR,
	Rating FLOAT,
	JmlPesananSelesai INT,
	PRIMARY KEY (Id),
  FOREIGN KEY (Id) REFERENCES PENGGUNA(Id)
);
-- ASUMSI - NoHP hanya maksimal 16 digit, dan NPWP pasti 16 digit

-- tabel 5
CREATE TABLE KATEGORI_TR_MYPAY(
    Id UUID,
    Nama VARCHAR(50),
    PRIMARY KEY (Id)
);

-- tabel 4
CREATE TABLE TR_MYPAY (
	Id UUID,
	UserId UUID,
	Tgl DATE,
	Nominal DECIMAL,
	KategoriId UUID,
  
  PRIMARY KEY (Id),
	FOREIGN KEY (UserId) REFERENCES PENGGUNA(Id),
	FOREIGN KEY (KategoriId) REFERENCES KATEGORI_TR_MYPAY(Id)
);


-- tabel 6
CREATE TABLE KATEGORI_JASA (
		Id UUID PRIMARY KEY,
  	NamaKategori VARCHAR
);

-- tabel 7
CREATE TABLE PEKERJA_KATEGORI_JASA (
    PekerjaId UUID,
    KategoriJasaId UUID,
    PRIMARY KEY (PekerjaId, KategoriJasaId),
    FOREIGN KEY (PekerjaId) REFERENCES PEKERJA(id),
    FOREIGN KEY (KategoriJasaId) REFERENCES KATEGORI_JASA(id)
);

-- tabel 8
CREATE TABLE SUBKATEGORI_JASA (
    Id UUID PRIMARY KEY,
    NamaSubkategori VARCHAR,
    Deskripsi TEXT,
    KategoriJasaId UUID,
    FOREIGN KEY (KategoriJasaId) REFERENCES KATEGORI_JASA(Id)
);

-- tabel 9
CREATE TABLE SESI_LAYANAN (
    SubkategoriId UUID,
    Sesi INT,
    Harga DECIMAL,
    PRIMARY KEY (SubkategoriId, Sesi),
    FOREIGN KEY (SubkategoriId) REFERENCES SUBKATEGORI_JASA(Id)
);

-- tabel 10
CREATE TABLE DISKON(
		Kode VARCHAR(50) PRIMARY KEY,
    Potongan DECIMAL NOT NULL CHECK (Potongan >= 0),
    MinTrPemesanan INT NOT NULL CHECK (MinTrPemesanan >= 0)
);

-- tabel 11
CREATE TABLE VOUCHER(
    Kode VARCHAR(50),
    JmlHariBerlaku INT NOT NULL CHECK (JmlHariBerlaku >= 0),
    KuotaPenggunaan INT,
    Harga DECIMAL NOT NULL CHECK  (Harga >= 0),
    PRIMARY KEY (Kode),
    FOREIGN KEY (Kode) REFERENCES DISKON (Kode)
);

-- tabel 12
CREATE TABLE PROMO(
    Kode VARCHAR(50),
    TglAkhirBerlaku DATE NOT NULL,
    PRIMARY KEY (Kode),
    FOREIGN KEY (Kode) REFERENCES DISKON (Kode)
);

-- tabel 15
CREATE TABLE METODE_BAYAR(
    Id UUID PRIMARY KEY, 
    Nama VARCHAR(50) NOT NULL
);

-- tabel 13
CREATE TABLE TR_PEMBELIAN_VOUCHER(
    Id UUID,
    TglAwal DATE NOT NULL,
    TglAkhir DATE NOT NULL,
    TelahDigunakan INT NOT NULL CHECK (TelahDigunakan >= 0),
    IdPelanggan UUID,
    IdVoucher VARCHAR(50),
    IdMetodeBayar UUID,
    PRIMARY KEY (Id),
    FOREIGN KEY (IdPelanggan) REFERENCES PELANGGAN (Id),
    FOREIGN KEY (IdVoucher) REFERENCES VOUCHER (Kode),
    FOREIGN KEY (IdMetodeBayar) REFERENCES METODE_BAYAR (Id)
);

-- tabel 14
CREATE TABLE TR_PEMESANAN_JASA (
    Id UUID,
    TglPemesanan DATE NOT NULL,
    TglPekerjaan DATE NOT NULL,
    WaktuPekerjaan INTERVAL NOT NULL,
    TotalBiaya DECIMAL NOT NULL CHECK (TotalBiaya>=0),
    IdPelanggan UUID,
    IdPekerja UUID,
    IdKategoriJasa UUID,
    Sesi INT,
    IdDiskon VARCHAR(50),
    IdMetodeBayar UUID,
    PRIMARY KEY (Id),
    FOREIGN KEY (IdPelanggan) REFERENCES PELANGGAN (Id),
    FOREIGN KEY (IdPekerja) REFERENCES PEKERJA (Id),
    FOREIGN KEY (IdKategoriJasa,Sesi) REFERENCES SESI_LAYANAN (SubkategoriId,Sesi),
    FOREIGN KEY (IdDiskon) REFERENCES DISKON (Kode),
    FOREIGN KEY (IdMetodeBayar) REFERENCES METODE_BAYAR (Id)
);
-- ASUMSI - tipe datetime pada WaktuPekerjaan adalah interval waktu lamanya pengerjaan.

-- tabel 16
CREATE TABLE STATUS_PESANAN(
    Id UUID, 
    Status VARCHAR(50) NOT NULL,
    PRIMARY KEY (Id)
);

-- tabel 17
CREATE TABLE TR_PEMESANAN_STATUS(
    IdTrPemesanan UUID,
    IdStatus UUID,
    TglWaktu TIMESTAMP NOT NULL,
    PRIMARY KEY (IdTrPemesanan,IdStatus),
    FOREIGN KEY (IdTrPemesanan) REFERENCES TR_PEMESANAN_JASA (Id),
    FOREIGN KEY (IdStatus) REFERENCES STATUS_PESANAN (Id)
);
-- ASUMSI - tipe datetime pada TglWaktu adalah tanggal dan juga waktu status_pesanan dibuat/berubah.

-- tabel 18
CREATE TABLE TESTIMONI(
    IdTrPemesanan UUID,
    Tgl DATE,
    Teks TEXT,
    Rating INT NOT NULL DEFAULT 0,
    PRIMARY KEY (IdTrPemesanan,Tgl),
    FOREIGN KEY (IdTrPemesanan) REFERENCES TR_PEMESANAN_JASA (Id)
);
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- DUMMY DATA PENGGUNA TABEL 1
INSERT INTO PENGGUNA VALUES 
(uuid_generate_v4(), 'Edmond Christian', 'L', '0800000', 'pwku123', '2005-12-25', 'Jl. alamat ku disini', 99999),
(uuid_generate_v4(), 'Daffa Naufal', 'L', '08010101', 'capyblapy', '2005-02-25', 'Bikini Bottom Regency', 69),
(uuid_generate_v4(), 'Emilia', 'P', '081111', 'gatauapaanlah', '1875-05-15', 'Re zero season 3', 1554322),
(uuid_generate_v4(), 'nama', 'L', '0822222', 'pwd', '1929-02-28', 'alamat', 1),
(uuid_generate_v4(), 'Andi', 'L', '08234567890', 'password123', '1990-05-15', 'Jl. Merdeka No. 1', 10000.00),
(uuid_generate_v4(), 'Budi', 'L', '08298765432', 'mypassword', '1995-08-20', 'Jl. Pahlawan No. 2', 15050.00),
(uuid_generate_v4(), 'Citra', 'P', '08213579864', 'securepass', '1988-03-10', 'Jl. Jendral Sudirman No. 3', 20000.00),
(uuid_generate_v4(), 'Diana', 'P', '08214523678', 'dianapwd', '1993-12-01', 'Jl. Soekarno No. 4', 7575.00),
(uuid_generate_v4(), 'Eko', 'L', '08225678901', 'ekopass', '1992-11-30', 'Jl. Kebangsaan No. 5', 5000.00),
(uuid_generate_v4(), 'Fani', 'P', '08237894567', 'fanipwd', '1991-04-22', 'Jl. Ahmad Yani No. 6', 30000.00);

-- DUMMY DATA PELANGGAN TABEL 2
INSERT INTO PELANGGAN VALUES
((SELECT Id FROM PENGGUNA WHERE nama='Emilia'), 'Gold'),
((SELECT Id FROM PENGGUNA WHERE nama='nama'), 'Obsidian'),
((SELECT Id FROM PENGGUNA WHERE nama='Eko'), 'Silver'),
((SELECT Id FROM PENGGUNA WHERE nama='Andi'), 'Bronze'),
((SELECT Id FROM PENGGUNA WHERE nama='Budi'), 'Gold');

-- DUMMY DATA PEKERJA TABEL 3
INSERT INTO PEKERJA VALUES
((SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian'), 'Bank Indo', '1234567890234523', '1234567890876542', 'link foto edmon', 5.0, 543243),
((SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal'), 'PacilBank', '1234567890231111', '3214567890876542', 'link foto dafa', 5.0, 777),
((SELECT Id FROM PENGGUNA WHERE nama='Citra'), 'Bang siomay bang', '1234567890232222', '3334567890876542', 'link foto citra', 3.3, 69),
((SELECT Id FROM PENGGUNA WHERE nama='Diana'), 'BNI', '1234567890233333', '1111567890876542', 'link foto diana', 4.3, 98),
((SELECT Id FROM PENGGUNA WHERE nama='Fani'), 'Mandiri', '1234567890233232', '1234555890876542', 'link foto fani', 2.1, 2);

-- DUMMY DATA KATEGORI_TR_MYPAY TABEL 5
INSERT INTO KATEGORI_TR_MYPAY VALUES 
(uuid_generate_v4(), 'Topup MyPay'),
(uuid_generate_v4(), 'Membayar transaksi jasa'),
(uuid_generate_v4(), 'Transfer MyPay ke pengguna lain'),
(uuid_generate_v4(), 'Menerima honor transaksi jasa'),
(uuid_generate_v4(), 'Withdrawal MyPay ke rekening bank');

-- DUMMY DATA TR_MYPAY TABEL 4
INSERT INTO TR_MYPAY VALUES
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), '2024-10-10', 1, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Topup MyPay')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), '2024-11-11', 2, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Membayar transaksi jasa')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='nama'), '2024-12-02', 3, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Topup MyPay')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Fani'), '2024-10-25', 4, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Menerima honor transaksi jasa')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='nama'), '2025-01-01', 5, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Withdrawal MyPay ke rekening bank')),

(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Eko'), '2024-05-05', 6, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Topup MyPay')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Citra'), '2024-05-06', 7, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Transfer MyPay ke pengguna lain')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Eko'), '2024-05-06', 8, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Membayar transaksi jasa')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal'), '2024-09-11', 9, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Topup MyPay')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal'), '2024-09-11', 10, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Withdrawal MyPay ke rekening bank')),

(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Citra'), '2023-10-23', 11, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Topup MyPay')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Budi'), '2023-10-23', 12, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Transfer MyPay ke pengguna lain')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Budi'), '2023-10-23', 13, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Transfer MyPay ke pengguna lain')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Budi'), '2023-10-23', 14, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Membayar transaksi jasa')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Andi'), '2023-10-23', 15, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Membayar transaksi jasa')),

(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian'), '2024-10-10', 16, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Topup MyPay')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Diana'), '2024-10-10', 17, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Menerima honor transaksi jasa')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Diana'), '2024-10-10', 18, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Transfer MyPay ke pengguna lain')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), '2024-10-10', 19, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Withdrawal MyPay ke rekening bank')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian'), '2024-10-10', 1000000000, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Withdrawal MyPay ke rekening bank')),

(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='nama'), '2024-08-05', 21, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Topup MyPay')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='nama'), '2024-04-06', 22, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Transfer MyPay ke pengguna lain')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Andi'), '2024-04-06', 23, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Membayar transaksi jasa')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal'), '2024-08-17', 123, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Topup MyPay')),
(uuid_generate_v4(), (SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal'), '1945-08-17', 123456789, (SELECT Id FROM KATEGORI_TR_MYPAY WHERE nama='Withdrawal MyPay ke rekening bank'));


-- DUMMY DATA TABEL 6 (5)
INSERT INTO KATEGORI_JASA VALUES
(uuid_generate_v4(), 'Home Cleaning'),
(uuid_generate_v4(), 'Deep Cleaning'),
(uuid_generate_v4(), 'Service AC'),
(uuid_generate_v4(), 'Massage'),
(uuid_generate_v4(), 'Hair Care');

-- DUMMY DATA TABEL 7 (10)
INSERT INTO PEKERJA_KATEGORI_JASA VALUES
((SELECT Id FROM PEKERJA WHERE NPWP='1234567890876542'), (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Home Cleaning')),
((SELECT Id FROM PEKERJA WHERE NPWP='1234567890876542'), (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Deep Cleaning')),
((SELECT Id FROM PEKERJA WHERE NPWP='3214567890876542'), (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Deep Cleaning')),
((SELECT Id FROM PEKERJA WHERE NPWP='3214567890876542'), (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Service AC')),
((SELECT Id FROM PEKERJA WHERE NPWP='3334567890876542'), (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Service AC')),
((SELECT Id FROM PEKERJA WHERE NPWP='3334567890876542'), (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Massage')),
((SELECT Id FROM PEKERJA WHERE NPWP='1111567890876542'), (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Massage')),
((SELECT Id FROM PEKERJA WHERE NPWP='1111567890876542'), (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Hair Care')),
((SELECT Id FROM PEKERJA WHERE NPWP='1234555890876542'), (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Hair Care')),
((SELECT Id FROM PEKERJA WHERE NPWP='1234555890876542'), (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Home Cleaning'));

-- DUMMY DATA TABEL 8 (10)
INSERT INTO SUBKATEGORI_JASA VALUES
(uuid_generate_v4(), 'Daily Cleaning', 'Membersihkan hunian secara umum seperti menyapu, mengepel, dan mengelap', (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Home Cleaning')),
(uuid_generate_v4(), 'Setrika', 'Menyetrika dan melipat pakaian menggunakan peralatan pribadi pelanggan', (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Home Cleaning')),
(uuid_generate_v4(), 'Pembersihan dapur dan kulkas', 'Membersihkan kulkas dan dapur beserta peralatannya', (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Home Cleaning')),
(uuid_generate_v4(), 'Kombo daily cleaning dan setrika', 'Membersihkan hunian secara umum dan juga menyetrika serta melipat segala jenis pakaian', (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Home Cleaning')),
(uuid_generate_v4(), 'Kombo daily cleaning dan dapur', 'Membersihkan hunian secara umum dan juga membersihkan dapur beserta peralatannya', (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Home Cleaning')),
(uuid_generate_v4(), 'Cuci kasur', 'Mencuci dan membersihkan kasur, bantal, guling, dan sprei dari noda dan kotoran', (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Deep Cleaning')),
(uuid_generate_v4(), 'Cuci sofa', 'Mencuci dan menghisap debu sofa pelanggan', (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Deep Cleaning')),
(uuid_generate_v4(), 'Cuci karpet', 'Mencuci dan mengeringkan karpet pelanggan dari noda dan debu', (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Deep Cleaning')),
(uuid_generate_v4(), 'Cuci tirai', 'Mencuci tirai pelanggan dari debu dan kotoran', (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Deep Cleaning')),
(uuid_generate_v4(), 'Bersih kamar mandi', 'Membersihkan kamar mandi dengan menyikat dan pembersihan kerak pada lantai', (SELECT Id FROM KATEGORI_JASA WHERE NamaKategori='Deep Cleaning'));

-- DUMMY DATA TABEL 9, (30)
INSERT INTO SESI_LAYANAN VALUES
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning'), 1, 65000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning'), 2, 115000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning'), 3, 165000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning'), 4, 215000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning'), 5, 265000),

((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika'), 1, 75000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika'), 2, 115000),

((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Pembersihan dapur dan kulkas'), 1, 95000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Pembersihan dapur dan kulkas'), 2, 145000),

((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan setrika'), 2, 200000),

((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan dapur'), 2, 220000),

((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa'), 1, 98500),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa'), 2, 162500),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa'), 3, 230000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa'), 4, 270000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa'), 5, 300000),

((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur'), 1, 85000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur'), 2, 155000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur'), 3, 215000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur'), 4, 250000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur'), 5, 280000),

((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci karpet'), 1, 60000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci karpet'), 2, 100000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci karpet'), 3, 150000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci karpet'), 4, 190000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci karpet'), 5, 230000),

((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci tirai'), 1, 70000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci tirai'), 2, 115000),

((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Bersih kamar mandi'), 1, 100000),
((SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Bersih kamar mandi'), 2, 175000);



-- DUMMY DATA TABEL 10, (20)
INSERT INTO DISKON VALUES
('UNTUNG10', 10000.00, 100000),
('UNTUNG20', 20000.00, 150000),
('UNTUNG30', 30000.00, 200000),
('UNTUNG40', 40000.00, 225000),

('GAJISEP24', 20000.00, 150000),
('GAJIOKT24', 25000.00, 175000),
('GAJINOV24', 30000.00, 175000),
('GAJIDES24', 50000.00, 200000),

('PROMO25', 25000.00, 250000),
('PROMO15', 15000.00, 150000),
('PROMO10', 10000.00, 100000),
('PROMO50', 50000.00, 300000),

('SAVE30', 30000.00, 100000),
('SAVE70', 70000.00, 200000),
('SAVE90', 90000.00, 300000),
('SAVE50', 50000.00, 150000),

('BERKAH1', 500000.00, 10000000),
('BERKAH2', 1000000.00, 12500000),
('BERKAH3', 1500000.00, 15000000),
('BERKAH4', 1750000.00, 20000000);



-- DUMMY DATA TABEL 11, 10 data
INSERT INTO VOUCHER VALUES 
('PROMO25', 14, 5, 25000.00),
('PROMO15', 14, 3, 15000.00),
('PROMO10', 14, 3, 10000.00),
('PROMO50', 14, 5, 50000.00),
('UNTUNG10', 30, 2, 30000.00),
('UNTUNG20', 30, 3, 40000.00),
('UNTUNG30', 30, 4, 50000.00),
('UNTUNG40', 30, 5, 60000.00),
('SAVE70', 7, 3, 35000.00),
('SAVE90', 7, 3, 45000.00);



-- DUMMY DATA TABEL 12, 10 data
INSERT INTO PROMO VALUES 
('GAJISEP24', '2024-9-30'),
('GAJIOKT24', '2024-10-31'),
('GAJINOV24', '2024-11-30'),
('GAJIDES24', '2024-12-31'),
('SAVE30', '2024-11-11'),
('SAVE50', '2024-12-12'),
('BERKAH1', '2024-12-25'),
('BERKAH2', '2025-1-1'),
('BERKAH3', '2025-6-9'),
('BERKAH4', '2025-12-25');



-- DUMMY DATA TABEL 13, 18 data
INSERT INTO TR_PEMBELIAN_VOUCHER VALUES 
(uuid_generate_v4(), '2024-10-1', '2025-10-15','0', (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), 'PROMO25', (SELECT Id from METODE_BAYAR WHERE nama='MyPay')),
(uuid_generate_v4(), '2024-10-10', '2025-10-24','2', (SELECT Id FROM PENGGUNA WHERE nama='nama'), 'PROMO25', (SELECT Id from METODE_BAYAR WHERE nama='GoPay')),
(uuid_generate_v4(), '2024-10-20', '2025-11-3','1', (SELECT Id FROM PENGGUNA WHERE nama='Eko'), 'PROMO15', (SELECT Id from METODE_BAYAR WHERE nama='MyPay')),
(uuid_generate_v4(), '2024-10-23', '2025-11-6','4', (SELECT Id FROM PENGGUNA WHERE nama='nama'), 'PROMO50', (SELECT Id from METODE_BAYAR WHERE nama='OVO')),
(uuid_generate_v4(), '2024-10-18', '2025-11-1','2', (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), 'PROMO10', (SELECT Id from METODE_BAYAR WHERE nama='MyPay')),
(uuid_generate_v4(), '2024-10-16', '2025-10-30','2', (SELECT Id FROM PENGGUNA WHERE nama='Andi'), 'PROMO10', (SELECT Id from METODE_BAYAR WHERE nama='Virtual Account BCA')),

(uuid_generate_v4(), '2024-10-1', '2025-10-31','0', (SELECT Id FROM PENGGUNA WHERE nama='Budi'), 'UNTUNG10', (SELECT Id from METODE_BAYAR WHERE nama='Virtual Account BNI')),
(uuid_generate_v4(), '2024-10-2', '2025-11-1','1', (SELECT Id FROM PENGGUNA WHERE nama='Eko'), 'UNTUNG10', (SELECT Id from METODE_BAYAR WHERE nama='Virtual Account Mandiri')),
(uuid_generate_v4(), '2024-10-9', '2025-11-8','2', (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), 'UNTUNG20', (SELECT Id from METODE_BAYAR WHERE nama='MyPay')),
(uuid_generate_v4(), '2024-10-11', '2025-11-10','0', (SELECT Id FROM PENGGUNA WHERE nama='nama'), 'UNTUNG20', (SELECT Id from METODE_BAYAR WHERE nama='GoPay')),
(uuid_generate_v4(), '2024-10-19', '2025-11-18','3', (SELECT Id FROM PENGGUNA WHERE nama='Andi'), 'UNTUNG30', (SELECT Id from METODE_BAYAR WHERE nama='OVO')),
(uuid_generate_v4(), '2024-11-1', '2025-12-1','4', (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), 'UNTUNG40', (SELECT Id from METODE_BAYAR WHERE nama='GoPay')),

(uuid_generate_v4(), '2024-11-1', '2025-11-8','2', (SELECT Id FROM PENGGUNA WHERE nama='Andi'), 'SAVE70', (SELECT Id from METODE_BAYAR WHERE nama='Virtual Account Mandiri')),
(uuid_generate_v4(), '2024-10-1', '2025-10-8','0', (SELECT Id FROM PENGGUNA WHERE nama='Budi'), 'SAVE70', (SELECT Id from METODE_BAYAR WHERE nama='Virtual Account BNI')),
(uuid_generate_v4(), '2024-10-10', '2025-10-17','1', (SELECT Id FROM PENGGUNA WHERE nama='Eko'), 'SAVE90', (SELECT Id from METODE_BAYAR WHERE nama='Virtual Account BCA')),
(uuid_generate_v4(), '2024-10-20', '2025-10-27','0', (SELECT Id FROM PENGGUNA WHERE nama='nama'), 'SAVE90', (SELECT Id from METODE_BAYAR WHERE nama='MyPay')),
(uuid_generate_v4(), '2024-11-5', '2025-12-5','0', (SELECT Id FROM PENGGUNA WHERE nama='Andi'), 'UNTUNG40', (SELECT Id from METODE_BAYAR WHERE nama='GoPay')),
(uuid_generate_v4(), '2024-10-5', '2025-11-4','2', (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), 'PROMO15', (SELECT Id from METODE_BAYAR WHERE nama='MyPay'));



-- Dummy data METODE_BAYAR TABEL 15
INSERT INTO METODE_BAYAR VALUES 
(uuid_generate_v4(), 'MyPay'),
(uuid_generate_v4(), 'GoPay'),
(uuid_generate_v4(), 'OVO'),
(uuid_generate_v4(), 'Virtual Account BCA'),
(uuid_generate_v4(), 'Virtual Account BNI'),
(uuid_generate_v4(), 'Virtual Account Mandiri');



-- Dummy data TR_PEMESANAN_JASA TABEL 14, 25 data
INSERT INTO TR_PEMESANAN_JASA VALUES
(uuid_generate_v4(), '2024-11-17', '2024-11-19', '2h 30m 00s', 225000, (SELECT Id FROM PENGGUNA WHERE nama='Andi'), (SELECT Id FROM PENGGUNA WHERE nama='Diana'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning'), 5,'UNTUNG40', (SELECT Id FROM METODE_BAYAR WHERE Nama='Virtual Account BCA')),
(uuid_generate_v4(), '2024-11-13', '2024-11-15', '2h 30m 00s', 245000, (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), (SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning'), 5,'UNTUNG20', (SELECT Id FROM METODE_BAYAR WHERE Nama='GoPay')),
(uuid_generate_v4(), '2024-11-19', '2024-11-21', '2h 30m 00s', 215000, (SELECT Id FROM PENGGUNA WHERE nama='Budi'), (SELECT Id FROM PENGGUNA WHERE nama='Fani'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning'), 5,'SAVE50', (SELECT Id FROM METODE_BAYAR WHERE Nama='Virtual Account Mandiri')),
(uuid_generate_v4(), '2024-11-15', '2024-11-17', '2h 30m 00s', 235000, (SELECT Id FROM PENGGUNA WHERE nama='nama'), (SELECT Id FROM PENGGUNA WHERE nama='Citra'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning'), 5,'UNTUNG30', (SELECT Id FROM METODE_BAYAR WHERE Nama='OVO')),
(uuid_generate_v4(), '2024-11-11', '2024-11-13', '2h 30m 00s', 255000, (SELECT Id FROM PENGGUNA WHERE nama='Eko'), (SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning'), 5,'UNTUNG10', (SELECT Id FROM METODE_BAYAR WHERE Nama='MyPay')),

(uuid_generate_v4(), '2024-10-13', '2024-10-15', '1h 00m 00s', 105000, (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), (SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika'), 2,'PROMO10', (SELECT Id FROM METODE_BAYAR WHERE Nama='GoPay')),
(uuid_generate_v4(), '2024-10-19', '2024-10-21', '1h 00m 00s', 105000, (SELECT Id FROM PENGGUNA WHERE nama='Budi'), (SELECT Id FROM PENGGUNA WHERE nama='Citra'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika'), 2,'UNTUNG10', (SELECT Id FROM METODE_BAYAR WHERE Nama='Virtual Account Mandiri')),
(uuid_generate_v4(), '2024-10-11', '2024-10-13', '1h 00m 00s', 105000, (SELECT Id FROM PENGGUNA WHERE nama='Eko'), (SELECT Id FROM PENGGUNA WHERE nama='Diana'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika'), 2,'UNTUNG10', (SELECT Id FROM METODE_BAYAR WHERE Nama='MyPay')),
(uuid_generate_v4(), '2024-10-17', '2024-10-19', '1h 00m 00s', 105000, (SELECT Id FROM PENGGUNA WHERE nama='Andi'), (SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika'), 2,'PROMO10', (SELECT Id FROM METODE_BAYAR WHERE Nama='Virtual Account BCA')),
(uuid_generate_v4(), '2024-10-15', '2024-10-17', '1h 00m 00s', 105000, (SELECT Id FROM PENGGUNA WHERE nama='nama'), (SELECT Id FROM PENGGUNA WHERE nama='Fani'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika'), 2,'UNTUNG10', (SELECT Id FROM METODE_BAYAR WHERE Nama='OVO')),

(uuid_generate_v4(), '2024-09-13', '2024-09-15', '3h 30m 00s', 170000, (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), (SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan setrika'), 2,'UNTUNG30', (SELECT Id FROM METODE_BAYAR WHERE Nama='GoPay')),
(uuid_generate_v4(), '2024-09-17', '2024-09-19', '3h 30m 00s', 180000, (SELECT Id FROM PENGGUNA WHERE nama='Andi'), (SELECT Id FROM PENGGUNA WHERE nama='Fani'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan setrika'), 2,'GAJISEP24', (SELECT Id FROM METODE_BAYAR WHERE Nama='Virtual Account BCA')),
(uuid_generate_v4(), '2024-09-15', '2024-09-17', '3h 30m 00s', 185000, (SELECT Id FROM PENGGUNA WHERE nama='nama'), (SELECT Id FROM PENGGUNA WHERE nama='Diana'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan setrika'), 2,'PROMO15', (SELECT Id FROM METODE_BAYAR WHERE Nama='OVO')),
(uuid_generate_v4(), '2024-09-19', '2024-09-21', '3h 30m 00s', 150000, (SELECT Id FROM PENGGUNA WHERE nama='Budi'), (SELECT Id FROM PENGGUNA WHERE nama='Citra'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan setrika'), 2,'GAJIDES24', (SELECT Id FROM METODE_BAYAR WHERE Nama='Virtual Account Mandiri')),
(uuid_generate_v4(), '2024-09-11', '2024-09-13', '3h 30m 00s', 130000, (SELECT Id FROM PENGGUNA WHERE nama='Eko'), (SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan setrika'), 2,'SAVE70', (SELECT Id FROM METODE_BAYAR WHERE Nama='MyPay')),

(uuid_generate_v4(), '2024-08-13', '2024-08-15', '2h 00m 00s', 230000, (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), (SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa'), 5,'SAVE70', (SELECT Id FROM METODE_BAYAR WHERE Nama='GoPay')),
(uuid_generate_v4(), '2024-08-11', '2024-08-13', '2h 00m 00s', 210000, (SELECT Id FROM PENGGUNA WHERE nama='Eko'), (SELECT Id FROM PENGGUNA WHERE nama='Fani'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa'), 5,'SAVE90', (SELECT Id FROM METODE_BAYAR WHERE Nama='MyPay')),
(uuid_generate_v4(), '2024-08-19', '2024-08-21', '2h 00m 00s', 250000, (SELECT Id FROM PENGGUNA WHERE nama='Budi'), (SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa'), 5,'GAJIDES24', (SELECT Id FROM METODE_BAYAR WHERE Nama='Virtual Account Mandiri')),
(uuid_generate_v4(), '2024-08-17', '2024-08-19', '2h 00m 00s', 260000, (SELECT Id FROM PENGGUNA WHERE nama='Andi'), (SELECT Id FROM PENGGUNA WHERE nama='Citra'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa'), 5,'UNTUNG40', (SELECT Id FROM METODE_BAYAR WHERE Nama='Virtual Account BCA')),
(uuid_generate_v4(), '2024-08-15', '2024-08-17', '2h 00m 00s', 250000, (SELECT Id FROM PENGGUNA WHERE nama='nama'), (SELECT Id FROM PENGGUNA WHERE nama='Diana'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa'), 5,'PROMO50', (SELECT Id FROM METODE_BAYAR WHERE Nama='OVO')),

(uuid_generate_v4(), '2024-07-13', '2024-07-15', '2h 30m 00s', 260000, (SELECT Id FROM PENGGUNA WHERE nama='Emilia'), (SELECT Id FROM PENGGUNA WHERE nama='Fani'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur'), 5,'GAJISEP24', (SELECT Id FROM METODE_BAYAR WHERE Nama='GoPay')),
(uuid_generate_v4(), '2024-07-11', '2024-07-13', '2h 30m 00s', 255000, (SELECT Id FROM PENGGUNA WHERE nama='Eko'), (SELECT Id FROM PENGGUNA WHERE nama='Citra'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur'), 5,'PROMO25', (SELECT Id FROM METODE_BAYAR WHERE Nama='MyPay')),
(uuid_generate_v4(), '2024-07-17', '2024-07-19', '2h 30m 00s', 230000, (SELECT Id FROM PENGGUNA WHERE nama='Andi'), (SELECT Id FROM PENGGUNA WHERE nama='Diana'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur'), 5,'SAVE50', (SELECT Id FROM METODE_BAYAR WHERE Nama='Virtual Account BCA')),
(uuid_generate_v4(), '2024-07-15', '2024-07-17', '2h 30m 00s', 210000, (SELECT Id FROM PENGGUNA WHERE nama='nama'), (SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur'), 5,'SAVE70', (SELECT Id FROM METODE_BAYAR WHERE Nama='OVO')),
(uuid_generate_v4(), '2024-07-19', '2024-07-21', '2h 30m 00s', 250000, (SELECT Id FROM PENGGUNA WHERE nama='Budi'), (SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal'), (SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur'), 5,'SAVE30', (SELECT Id FROM METODE_BAYAR WHERE Nama='Virtual Account Mandiri'));



-- Dummy data TR_PEMESANAN_JASA TABEL 16, 7 data
INSERT INTO STATUS_PESANAN VALUES
(uuid_generate_v4(),'Menunggu Pembayaran'),
(uuid_generate_v4(),'Mencari Pekerja'),
(uuid_generate_v4(),'Menunggu Pekerja'),
(uuid_generate_v4(),'Sedang Dikerjakan'),
(uuid_generate_v4(),'Selesai'),
(uuid_generate_v4(),'Terjadi Kesalahan pada Sistem'),
(uuid_generate_v4(),'Dibatalkan');



-- Dummy data TR_PEMESANAN_STATUS TABEL 17, 35 data
INSERT INTO TR_PEMESANAN_STATUS VALUES
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Andi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Diana') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pembayaran'), '2024-11-17 19:10:25-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Andi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Diana') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Mencari Pekerja'), '2024-11-17 20:10:25-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Andi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Diana') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pekerja'), '2024-11-18 12:10:25-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Andi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Diana') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Sedang Dikerjakan'), '2024-11-19 12:10:25-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Andi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Diana') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Selesai'), '2024-11-19 14:40:25-07'),

((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pembayaran'), '2024-11-13 19:15:25-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Mencari Pekerja'), '2024-11-13 20:15:25-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pekerja'), '2024-11-14 12:15:25-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Sedang Dikerjakan'), '2024-11-15 12:15:25-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Selesai'), '2024-11-15 14:45:25-07'),

((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Budi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Fani') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pembayaran'), '2024-11-19 19:17:23-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Budi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Fani') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Mencari Pekerja'), '2024-11-19 20:17:23-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Budi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Fani') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pekerja'), '2024-11-20 12:17:23-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Budi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Fani') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Sedang Dikerjakan'), '2024-11-21 12:17:23-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Budi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Fani') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Selesai'), '2024-11-21 14:47:23-07'),

((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='nama') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Citra') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pembayaran'), '2024-11-15 19:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='nama') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Citra') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Mencari Pekerja'), '2024-11-15 20:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='nama') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Citra') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pekerja'), '2024-11-16 12:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='nama') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Citra') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Sedang Dikerjakan'), '2024-11-17 12:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='nama') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Citra') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Selesai'), '2024-11-17 14:45:28-07'),

((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Eko') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pembayaran'), '2024-11-11 18:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Eko') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Mencari Pekerja'), '2024-11-11 19:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Eko') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pekerja'), '2024-11-12 11:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Eko') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Sedang Dikerjakan'), '2024-11-13 11:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Eko') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Selesai'), '2024-11-13 13:45:28-07'),

((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pembayaran'), '2024-10-11 17:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Mencari Pekerja'), '2024-10-11 18:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Menunggu Pekerja'), '2024-10-12 10:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Sedang Dikerjakan'), '2024-10-13 10:15:28-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Selesai'), '2024-10-13 11:15:28-07'),

((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan setrika')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Dibatalkan'), '2024-09-13 13:42:22-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Andi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Fani') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan setrika')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Dibatalkan'), '2024-09-13 21:12:11-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Terjadi Kesalahan pada Sistem'), '2024-08-13 19:12:58-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Eko') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Fani') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Terjadi Kesalahan pada Sistem'), '2024-08-13 21:05:38-07'),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Budi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci sofa')), (SELECT Id FROM STATUS_PESANAN WHERE Status='Terjadi Kesalahan pada Sistem'), '2024-08-13 13:12:22-07');



-- Dummy data TESTIMONI TABEL 18, 17 data
INSERT INTO TESTIMONI VALUES
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Andi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Diana') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), '2024-11-19', 'Mantap bersih banget', 5),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), '2024-11-15', 'Kinclong parah', 5),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Budi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Fani') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), '2024-11-21', 'Bersih sebersih hatiku', 5),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='nama') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Citra') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), '2024-11-17', 'APA APAAN KERJA GA BENER', 1),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Eko') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Daily Cleaning')), '2024-11-13', 'krg brsh', 4),

((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika')), '2024-10-15', 'anget ey bajunya', 5),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Budi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Citra') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika')), '2024-10-21', 'masih kusut bajunya', 3),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Eko') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Diana') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika')), '2024-10-13', 'wangi bajunya', 5),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Andi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika')), '2024-10-19', 'BAJUNYA GOSONG #$%!', 1),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='nama') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Fani') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Setrika')), '2024-10-17', 'masih kusut dikit', 4),

((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Emilia') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Fani') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur')), '2024-07-15', 'KASURNYA BERSIH SANGAT', 5),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Eko') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Citra') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur')), '2024-07-13', 'KASURNYA MASIH BASAH G**L*K', 1),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Andi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Diana') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur')), '2024-07-19', 'tidur jadi enak banget', 5),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='nama') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Edmond Christian') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur')), '2024-07-17', 'kurang bersih di pinggirnya', 4),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Budi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Cuci kasur')), '2024-07-21', 'lamaaaaaaaaaaaa', 2),

((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Budi') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Citra') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan setrika')), '2024-09-21', 'MAKASI KAK CITRA, RECOMMEND BGT', 3),
((SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPelanggan=(SELECT Id FROM PENGGUNA WHERE nama='Eko') AND IdPekerja=(SELECT Id FROM PENGGUNA WHERE nama='Daffa Naufal') AND IdKategoriJasa=(SELECT Id FROM SUBKATEGORI_JASA WHERE NamaSubkategori='Kombo daily cleaning dan setrika')), '2024-09-13', 'krn mz dapa', 5);



