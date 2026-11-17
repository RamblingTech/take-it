"""
forms.py: the add/edit form for devices.

A Django "form" knows which boxes to show, checks what people type
(e.g. "is this asset tag already taken?") and turns it into clean data.
"""

import datetime
from decimal import Decimal

from django import forms

from .models import CustomField, Device


class DeviceForm(forms.ModelForm):
    """
    The add/edit device form. A ModelForm builds its boxes straight from
    the Device model. On top of that, it adds one box per custom field.
    """

    class Meta:
        model = Device
        # The boxes shown, in this order. Holder and location are NOT here:
        # they change through check-out / check-in (step 3), so they stay accurate.
        fields = ["asset_tag", "serial", "name", "model", "status", "purchase_date", "notes"]
        widgets = {
            # Show a calendar date picker, and keep notes to a few lines.
            "purchase_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        # First let Django build the normal boxes...
        super().__init__(*args, **kwargs)

        # ...then add one box for each custom field the Admin has defined.
        self.custom_fields = list(CustomField.objects.all())
        for custom in self.custom_fields:
            box = self.make_box(custom)
            # Fill in the device's current value, if it has one.
            if self.instance.pk and custom.key in self.instance.custom_data:
                box.initial = self.instance.custom_data[custom.key]
            # Custom boxes are named "cf_<key>" so they never clash with normal ones.
            self.fields[f"cf_{custom.key}"] = box

        # Add Bootstrap's styling class to every box so the form looks tidy.
        for box in self.fields.values():
            css = "form-check-input" if isinstance(box.widget, forms.CheckboxInput) else "form-control"
            if isinstance(box.widget, forms.Select):
                css = "form-select"
            box.widget.attrs["class"] = css

    @staticmethod
    def make_box(custom):
        """Pick the right kind of form box for a custom field's type."""
        common = {"label": custom.name, "required": custom.required, "help_text": custom.help_text}
        if custom.field_type == CustomField.NUMBER:
            return forms.DecimalField(**common)
        if custom.field_type == CustomField.DATE:
            return forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), **common)
        if custom.field_type == CustomField.YES_NO:
            # A tick box can't be "required" (unticked just means No).
            common["required"] = False
            return forms.BooleanField(**common)
        if custom.field_type == CustomField.CHOICE:
            options = [("", "—")] + [(option, option) for option in custom.choice_list()]
            return forms.ChoiceField(choices=options, **common)
        return forms.CharField(max_length=500, **common)

    def custom_field_boxes(self):
        """The custom boxes only, so the page can show them under their own heading."""
        return [self[f"cf_{custom.key}"] for custom in self.custom_fields]

    def standard_boxes(self):
        """The normal boxes only."""
        return [self[name] for name in self.Meta.fields]

    def save(self, commit=True):
        device = super().save(commit=False)

        # Copy the custom answers into the device's custom_data dictionary.
        # Start from what's already there, so values for fields that were
        # removed later aren't thrown away.
        data = dict(device.custom_data)
        for custom in self.custom_fields:
            value = self.cleaned_data.get(f"cf_{custom.key}")
            # JSON can't store dates or decimals directly, so turn them into text/numbers.
            if isinstance(value, datetime.date):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = int(value) if value == value.to_integral_value() else float(value)
            if value in (None, ""):
                data.pop(custom.key, None)
            else:
                data[custom.key] = value
        device.custom_data = data

        if commit:
            device.save()
        return device
