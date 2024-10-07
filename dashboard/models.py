from django.db import models
from properties.models import Property
from django.contrib.auth.models import User

class UserActionLog(models.Model):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    
    ACTION_TYPES = [
        (CREATE, 'Created'),
        (UPDATE, 'Updated'),
        (DELETE, 'Deleted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='user_actions', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} {self.get_action_type_display()} {self.property.title if self.property else "a property"} on {self.timestamp}'
