from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class conversation(models.Model ):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    
    prompt=models.CharField(max_length=256)
    responde=models.CharField(max_length=256)

