from django.db import models

class Leaf(models.Model):
    # Image uploaded by user (of the leaf) (((((no need to applay not null constaint cuz django already assumes that)))))
    img = models.ImageField(upload_to='leafs/')

    #class name ['healthy','bacterial_spot',etc]
    leaf_diagnose = models.CharField(max_length=100, blank=True, null=True)
    
    # Prediction confidence percentage (e.g., 0.98 = 98%)
    confidence = models.FloatField(default=0.0)
    
    # Timestamp
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.leaf_diagnose or 'Unknown'} - {self.confidence:.2%}"
    
