-- Students table
CREATE TABLE Students (
    Admission_Number VARCHAR(20) PRIMARY KEY,
    S_Name VARCHAR(255),
    NFC_UID VARCHAR(50) UNIQUE,
    Password VARCHAR(255)
);

-- Books table
CREATE TABLE Books (
    Book_ID INT PRIMARY KEY IDENTITY,
    Title VARCHAR(255),
    Author VARCHAR(255),
    Total_Copies INT,
    Available INT,
    NFC_UID VARCHAR(50) UNIQUE,
    ImageURL VARCHAR(MAX)
);


-- Issue Register table
CREATE TABLE Issue_Register (
    Issue_ID INT PRIMARY KEY IDENTITY,
    Admission_Number VARCHAR(20),
    Book_ID INT,
    Issue_Date DATE,
    Due_Date DATE,
    Return_Date DATE,
    FOREIGN KEY (Admission_Number) REFERENCES Students(Admission_Number),
    FOREIGN KEY (Book_ID) REFERENCES BOOKS(Book_ID)
);

INSERT INTO BOOKS VALUES('The Martian', 'Andy Weir',1,1);

SELECT * FROM BOOKS

SELECT * FROM Students

SELECT * FROM Issue_Register;

UPDATE Books SET NFC_UID = 'NULL' WHERE Book_ID = 2

UPDATE Students SET NFC_UID = '132E5903' WHERE Admission_Number = '2924PS'

CREATE TRIGGER UpdateAvailableStatus
ON Issue_Register
AFTER INSERT, UPDATE
AS
BEGIN
    IF EXISTS (SELECT 1 FROM inserted WHERE Return_Date IS NULL)
    BEGIN
        UPDATE Books
        SET Available = 0
        FROM Books
        INNER JOIN inserted ON Books.Book_ID = inserted.Book_ID;
    END

    IF EXISTS (SELECT 1 FROM inserted WHERE Return_Date IS NOT NULL)
    BEGIN
        UPDATE Books
        SET Available = 1
        FROM Books
        INNER JOIN inserted ON Books.Book_ID = inserted.Book_ID;
    END
END;
