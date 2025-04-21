from django.db import models
class Account(models.Model):
    userid = models.CharField(db_column='userID', primary_key=True, max_length=100)  # Field name made lowercase.
    firstname = models.CharField(db_column='firstName', max_length=100)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=100)  # Field name made lowercase.
    userpass = models.CharField(db_column='userPass', max_length=256, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'account'
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Announcements(models.Model):
    announcementid = models.AutoField(db_column='announcementID', primary_key=True)  # Field name made lowercase.
    employerid = models.ForeignKey(Account, models.DO_NOTHING, db_column='employerID', blank=True, null=True)  # Field name made lowercase.
    announcement = models.TextField(blank=True, null=True)
    announcementtime = models.DateTimeField(db_column='announcementTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'announcements'
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Break(models.Model):
    breakid = models.AutoField(db_column='breakID', primary_key=True)  # Field name made lowercase.
    shiftid = models.ForeignKey('Shifttime', models.DO_NOTHING, db_column='shiftID')  # Field name made lowercase.
    breakstart = models.DateTimeField(db_column='breakStart', blank=True, null=True)  # Field name made lowercase.
    breakend = models.DateTimeField(db_column='breakEnd', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'break'
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Company(models.Model):
    id = models.AutoField(primary_key=True)  # Artificial primary key for Django
    employerid = models.OneToOneField(Account, models.DO_NOTHING, db_column='employerID')  # Field name made lowercase. The composite primary key (employerID, companyID) found, that is not supported. The first column is selected.
    companyid = models.CharField(db_column='companyID', unique=True, max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'company'
        constraints = [
            models.UniqueConstraint(fields=['employerid', 'companyid'], name='companyPK')
        ]
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Compensation(models.Model):
    shiftid = models.OneToOneField('Shifttime', models.DO_NOTHING, db_column='shiftID', primary_key=True)  # Field name made lowercase.
    employeeid = models.ForeignKey(Account, models.DO_NOTHING, db_column='employeeID')  # Field name made lowercase.
    shiftcompensation = models.DecimalField(db_column='shiftCompensation', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'compensation'
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Employed(models.Model):
    id = models.AutoField(primary_key=True)  # Artificial primary key for Django
    employeeid = models.OneToOneField(Account, models.DO_NOTHING, db_column='employeeID')  # Field name made lowercase. The composite primary key (employeeID, companyID) found, that is not supported. The first column is selected.
    companyid = models.ForeignKey(Company, models.DO_NOTHING, db_column='companyID', to_field='companyid')  # Field name made lowercase.
    userrole = models.ForeignKey('Roletable', models.DO_NOTHING, db_column='userRole', blank=True, null=True)  # Field name made lowercase.
    usersalary = models.DecimalField(db_column='userSalary', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'employed'
        constraints = [
            models.UniqueConstraint(fields=['employeeid', 'companyid'], name='employedPK')
        ]
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Expenses(models.Model):
    id = models.AutoField(primary_key=True)  # Artificial primary key for Django
    employerid = models.OneToOneField(Account, models.DO_NOTHING, db_column='employerID')  # Field name made lowercase. The composite primary key (employerID, expenseDate) found, that is not supported. The first column is selected.
    expensedate = models.DateField(db_column='expenseDate')  # Field name made lowercase.
    expense = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'expenses'
        constraints = [
            models.UniqueConstraint(fields=['employerid', 'expensedate'], name='expensesPK')
        ]
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Notices(models.Model):
    id = models.AutoField(primary_key=True)  # Artificial primary key for Django
    employeeid = models.OneToOneField(Account, models.DO_NOTHING, db_column='employeeID')  # Field name made lowercase. The composite primary key (employeeID, announcementID) found, that is not supported. The first column is selected.
    announcementid = models.ForeignKey(Announcements, models.DO_NOTHING, db_column='announcementID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'notices'
        constraints = [
            models.UniqueConstraint(fields=['employeeid', 'announcementid'], name='noticesPK')
        ]
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Roletable(models.Model):
    userrole = models.CharField(db_column='userRole', primary_key=True, max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'roletable'
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Schedules(models.Model):
    scheduleid = models.AutoField(db_column='scheduleID', primary_key=True)  # Field name made lowercase.
    employeeid = models.ForeignKey(Account, models.DO_NOTHING, db_column='employeeID')  # Field name made lowercase.
    starttime = models.DateTimeField(db_column='startTime', blank=True, null=True)  # Field name made lowercase.
    endtime = models.DateTimeField(db_column='endTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'schedules'
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Shifttime(models.Model):
    shiftid = models.AutoField(db_column='shiftID', primary_key=True)  # Field name made lowercase.
    employeeid = models.ForeignKey(Account, models.DO_NOTHING, db_column='employeeID')  # Field name made lowercase.
    clockin = models.DateTimeField(db_column='clockIn', blank=True, null=True)  # Field name made lowercase.
    clockout = models.DateTimeField(db_column='clockOut', blank=True, null=True)  # Field name made lowercase.
    breakduration = models.TimeField(db_column='breakDuration', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'shifttime'