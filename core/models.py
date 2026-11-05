
from django.db import models


class TradeTronSettings(models.Model):
    url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Enter the TradeTron URL."
    )

    is_enabled = models.BooleanField(
        default=True,
        help_text="Show or hide the TradeTron button on the user home page."
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "TradeTron Settings"

    class Meta:
        verbose_name = "TradeTron Settings"
        verbose_name_plural = "TradeTron Settings"
