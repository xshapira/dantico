from django.db import models

from tests.conf import JSON_FIELD_COMPATIBILITY, TEXT_CHOICES_COMPATIBILITY


class Category(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()


class Auction(models.Model):
    title = models.CharField(max_length=100)
    category = models.OneToOneField(
        Category, null=True, blank=True, on_delete=models.SET_NULL
    )
    start_date = models.DateField(auto_now=True)
    end_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Client(models.Model):
    key = models.CharField(max_length=20, unique=True)


class Profile(models.Model):
    address = models.TextField()
    dob = models.DateTimeField(null=True, blank=True)


class Group(models.Model):
    name = models.CharField(max_length=10)


class AgencyAdmin(models.Model):
    name = models.CharField(max_length=10)
    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        related_name="agency_admin",
        related_query_name="agency_admin",
    )


class UserType(models.Model):
    name = models.CharField(max_length=50)


class _UserABC(models.Model):
    full_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    tier = models.ForeignKey(
        UserType,
        on_delete=models.CASCADE,
        related_name="users",
        related_query_name="user",
        null=True,
    )

    groups = models.ManyToManyField(Group)

    class Meta:
        abstract = True


class User(_UserABC):
    ...


if TEXT_CHOICES_COMPATIBILITY:

    class UserTier(models.Model):
        class LevelOption(models.TextChoices):
            LEVEL_0 = "level-0"
            LEVEL_1 = "level-1"

        name = models.CharField(max_length=10)
        level = models.CharField(
            max_length=10, choices=LevelOption.choices, default=LevelOption.LEVEL_0
        )

    class User30(_UserABC):
        tier = models.ForeignKey(
            UserTier,
            on_delete=models.CASCADE,
            related_name="users",
            related_query_name="user",
            null=True,
        )


if JSON_FIELD_COMPATIBILITY:

    class JSONConfig(models.Model):
        config = models.JSONField(null=True)
