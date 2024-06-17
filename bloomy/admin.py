from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Package)
admin.site.register(Subscription)
admin.site.register(Specification)
admin.site.register(Order)
admin.site.register(Delivery)
