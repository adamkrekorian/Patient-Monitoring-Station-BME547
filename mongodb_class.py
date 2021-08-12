from pymodm import connect, MongoModel, fields


class Patient(MongoModel):
    patient_id = fields.IntegerField(primary_key=True)
    username = fields.CharField()


class MedInfo(MongoModel):
    unique_id = fields.UUIDField(primary_key=True)
    patient_id = fields.IntegerField()
    heart_rate = fields.IntegerField()
    ecg_data = fields.CharField()
    date_time = fields.DateTimeField()


class MedImg(MongoModel):
    unique_id = fields.UUIDField(primary_key=True)
    patient_id = fields.IntegerField()
    img_data = fields.CharField()
    date_time = fields.DateTimeField()
