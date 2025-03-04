CREATE TABLE Account
(
    userID varchar(100) NOT NULL,
    firstName varchar(100) NOT NULL,
    lastName varchar(100) NOT NULL,
    userPass varchar(64),
    PRIMARY KEY (userID),
    INDEX idx_fName (firstName),
    INDEX idx_lName (lastName)
)ENGINE = InnoDB;
CREATE TABLE Company
(
    employerID varchar(100) NOT NULL,
    companyID varchar(100) NOT NULL UNIQUE,
    FOREIGN KEY (employerID) REFERENCES Account(userID),
    CONSTRAINT companyPK PRIMARY KEY (employerID, companyID)
)ENGINE = InnoDB;
CREATE TABLE RoleTable
(
    userRole varchar(100),
    PRIMARY KEY (userRole)
)ENGINE = InnoDB;
CREATE TABLE Employed
(
    employeeID varchar(100) NOT NULL,
    companyID varchar(100) NOT NULL,
    userRole varchar(100),
    userSalary decimal(19,4),
    FOREIGN KEY (employeeID) REFERENCES Account(userID),
    FOREIGN KEY (companyID) REFERENCES Company(companyID),
    FOREIGN KEY (userRole) REFERENCES RoleTable(userRole),
    CONSTRAINT employedPK PRIMARY KEY (employeeID, companyID)
)ENGINE = InnoDB;
CREATE TABLE Schedules
(
    scheduleID int NOT NULL AUTO_INCREMENT,
    employeeID varchar(100) NOT NULL,
    startTime datetime DEFAULT NULL,
    endTime datetime DEFAULT NULL,
    FOREIGN KEY (employeeID) REFERENCES Account(userID),
    PRIMARY KEY (scheduleID),
    Index idx_employee (employeeID)
)ENGINE = InnoDB;
CREATE TABLE Expenses
(
    employerID varchar(100) NOT NULL,
    expenseDate DATE,
    expense decimal(19,4),
    FOREIGN KEY (employerID) REFERENCES Account(userID),
    CONSTRAINT expensesPK PRIMARY KEY (employerID, expenseDate)
)ENGINE = InnoDB;
CREATE TABLE ShiftTime
(
    shiftID int NOT NULL AUTO_INCREMENT,
    employeeID varchar(100) NOT NULL,
    clockIn datetime DEFAULT NULL,
    clockOut datetime DEFAULT NULL,
    breakDuration time DEFAULT 0,
    FOREIGN KEY (employeeID) REFERENCES Account(userID),
    PRIMARY KEY(shiftID),
    INDEX idx_employee (employeeID)
)ENGINE = InnoDB;
CREATE TABLE Compensation
(
    shiftID int NOT NULL,
    employeeID varchar(100) NOT NULL,
    shiftCompensation decimal(19,4),
    FOREIGN KEY (shiftID) REFERENCES ShiftTime(shiftID),
    FOREIGN KEY (employeeID) REFERENCES Account(userID),
    PRIMARY KEY (shiftID),
    INDEX idx_employee (employeeID)
)ENGINE = InnoDB;
CREATE TABLE Break
(
    breakID int NOT NULL AUTO_INCREMENT,
    shiftID int NOT NULL,
    breakStart datetime DEFAULT NULL,
    breakEnd datetime DEFAULT NULL,
    FOREIGN KEY (shiftID) REFERENCES ShiftTime(shiftID),
    PRIMARY KEY(breakID),
    INDEX idx_shift (shiftID)
)ENGINE = InnoDB;
CREATE TABLE announcements (
    announcementID int NOT NULL AUTO_INCREMENT,
    employerID varchar(100),
    announcement Text, 
    announcementTime datetime, 
    FOREIGN KEY (employerID) REFERENCES account(userID), 
    PRIMARY KEY(announcementID),
    Index idx_employer (employerID)
)ENGINE = InnoDB;
CREATE TABLE notices
(
    employeeID varchar(100),
    announcementID int NOT NULL,
    FOREIGN KEY (employeeID) REFERENCES account(userID),
    FOREIGN KEY (announcementID) REFERENCES announcements(announcementID),
    CONSTRAINT noticesPK PRIMARY KEY(employeeID, announcementID),
    Index idx_employee (employeeID)
)ENGINE = InnoDB;