from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from mptt.models import MPTTModel, TreeForeignKey


class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(_('email address'), unique=True, blank=False)
    REQUIRED_FIELDS = ['email', 'phone']


class Ad(models.Model):
    CHECKING = 10
    PUBLISHED = 20
    REJECTED = 30
    HIDDEN = 40

    STATUS = [
        (CHECKING, "checking"),
        (PUBLISHED, "publish"),
        (REJECTED, "rejected"),
        (HIDDEN, "hidden"),
    ]

    status = models.SmallIntegerField(choices=STATUS, default=CHECKING, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ads")
    title = models.CharField(max_length=60)
    category = TreeForeignKey('Category', on_delete=models.CASCADE, related_name='ads')
    description = models.TextField(max_length=5000)
    price = models.DecimalField(decimal_places=2, max_digits=15, default=0.0)
    contractual = models.BooleanField(default=False, blank=True)
    task_id = models.CharField(max_length=36, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return "Ad: {0}; creator: {1}; category {2}; price: {3};".format(self.title, self.creator,
                                                                         self.category, self.price)

class Category(MPTTModel):
    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = "categories"

    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def get_full_path(self):
        names = self.get_ancestors(include_self=True).values('name')
        full_name = ' - '.join(map(lambda x: x['name'], names))
        return full_name

    def __str__(self):
        return self.name


class Image(models.Model):
    image = models.ImageField(upload_to='ad_images/')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return "Image for {0}; creator: {1}".format(self.ad.title, self.ad.creator)


# class Favorite(models.Model):
#     favorite = models.ManyToManyField(Ad, related_name="favorites")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
#
#     def __str__(self):
#         return user.username
