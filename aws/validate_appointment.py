import json
from datetime import datetime, timedelta
import boto3

def lambda_handler(event, context):
    try:
        appointment = event['appointment']
        date = appointment['date']
        time = appointment['time']
        service_type = appointment['serviceType']
        
        # Convert appointment time to datetime
        appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        # Validate business hours (9 AM to 5 PM)
        hour = appointment_datetime.hour
        if hour < 9 or hour >= 17:
            return {
                'isValid': False,
                'message': 'Appointments must be scheduled between 9 AM and 5 PM'
            }
        
        # Validate weekday
        if appointment_datetime.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return {
                'isValid': False,
                'message': 'Appointments cannot be scheduled on weekends'
            }
        
        # Validate future date
        if appointment_datetime < datetime.now():
            return {
                'isValid': False,
                'message': 'Appointments must be scheduled for future dates'
            }
        
        # Check for existing appointments at the same time
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Appointments')
        
        response = table.query(
            IndexName='DateTimeIndex',
            KeyConditionExpression='#date = :date AND #time = :time',
            ExpressionAttributeNames={
                '#date': 'date',
                '#time': 'time'
            },
            ExpressionAttributeValues={
                ':date': date,
                ':time': time
            }
        )
        
        if response['Count'] > 0:
            return {
                'isValid': False,
                'message': 'This time slot is already booked'
            }
        
        # Validate service duration
        service_durations = {
            'oil-change': 60,  # minutes
            'tire-rotation': 45,
            'brake-service': 120,
            'general-inspection': 60,
            'repair': 180
        }
        
        duration = service_durations.get(service_type, 60)
        end_time = appointment_datetime + timedelta(minutes=duration)
        
        if end_time.hour >= 17:
            return {
                'isValid': False,
                'message': f'Service duration of {duration} minutes exceeds business hours'
            }
        
        return {
            'isValid': True,
            'message': 'Appointment validation successful'
        }
        
    except Exception as e:
        return {
            'isValid': False,
            'message': f'Validation error: {str(e)}'
        }
