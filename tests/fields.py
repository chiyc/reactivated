import enum

import pytest
import rest_framework
from django import forms
from django.apps.registry import Apps
from django.core.exceptions import ValidationError
from django.db.models import Model

from reactivated import constraints, fields
from sample.server.apps.samples import models


class EnumTest(enum.Enum):
    FIRST = "First"
    SECOND = "Second"
    THIRD = "Third"


def test_enum_form():
    class EnumForm(forms.ModelForm):
        class Meta:
            fields = ["hemisphere"]
            model = models.Continent

    form = EnumForm({"hemisphere": "NORTHERN"})

    assert form.is_valid()

    form = EnumForm({"hemisphere": "wrong"})
    assert form.is_valid() is False


def test_convert_enum_to_choices():
    (first_choice, first_label), (second_choice, second_label), (_, _) = list(
        fields.convert_enum_to_choices(EnumTest)
    )
    assert str(first_choice) == "FIRST"
    assert first_choice.choice == EnumTest.FIRST
    assert str(first_label) == "First"
    assert str(second_choice) == "SECOND"
    assert str(second_label) == "Second"
    assert second_choice.choice == EnumTest.SECOND


def test_parse_enum():
    assert fields.parse_enum(EnumTest, None) is None
    assert fields.parse_enum(EnumTest, "SECOND") is EnumTest.SECOND

    with pytest.raises(ValidationError, match=f"Invalid .* {EnumTest}"):
        fields.parse_enum(EnumTest, "FAKE")


def test_auto_contraint(settings):
    settings.INSTALLED_APPS = ["tests.fields"]
    test_apps = Apps(settings.INSTALLED_APPS)

    class TestModel(Model):
        enum_field = fields.EnumField(enum=EnumTest)

        class Meta:
            apps = test_apps

    constraint = TestModel._meta.constraints[0]
    assert isinstance(constraint, constraints.EnumConstraint)
    assert constraint.members == ["FIRST", "SECOND", "THIRD"]
    assert constraint.field_name == "enum_field"
    assert constraint.name == "fields_testmodel_enum_field_enum"


def test_drf_serializer(settings):
    settings.INSTALLED_APPS = ["tests.fields"]
    test_apps = Apps(settings.INSTALLED_APPS)

    class TestModel(Model):
        enum_field = fields.EnumField(enum=EnumTest)

        class Meta:
            apps = test_apps

    class TestModelSerializer(rest_framework.serializers.ModelSerializer):
        def create(self, validated_data):
            return validated_data

        def update(self, instance, validated_data):
            return validated_data

        class Meta:
            fields = "__all__"
            model = TestModel

    data = TestModelSerializer(TestModel(enum_field=EnumTest.SECOND)).data
    assert data["enum_field"] == "SECOND"

    data = TestModelSerializer({"enum_field": "SECOND"}).data
    assert data["enum_field"] == "SECOND"

    create_serializer = TestModelSerializer(data={"enum_field": "SECOND"})
    assert create_serializer.is_valid() is True
    validated_data = create_serializer.save()
    assert validated_data["enum_field"] == EnumTest.SECOND
    assert create_serializer.data["enum_field"] == "SECOND"

    update_serializer = TestModelSerializer(
        TestModel(enum_field=EnumTest.SECOND), data={"enum_field": "THIRD"}
    )
    assert update_serializer.is_valid() is True
    validated_data = update_serializer.save()
    assert validated_data["enum_field"] == EnumTest.THIRD
    assert update_serializer.data["enum_field"] == "THIRD"