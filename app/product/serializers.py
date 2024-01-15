from rest_framework import serializers
from .models import Category, Product, Property


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]


# Use when dealing directly with "Property" resource
class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ["id", "name", "value"]
        read_only_fields = ["id"]

    # Check for duplication error
    def validate(self, attrs):
        prop_exists = Property.objects.filter(
            name__iexact=attrs.get("name"),
            value__iexact=attrs.get("value"),
        ).exists()

        if prop_exists:
            msg = f"Property with this Name ({attrs["name"]}) and Value ({attrs["value"]}) already exists!"
            raise serializers.ValidationError(msg)

        return attrs


class NoValidationPropSerializer(PropertySerializer):
    """Property serializer without validation for duplication"""

    # Used when creating props through Product.
    # Skips duplication check cuz there's used get_or_create

    # Override to remove validation
    def validate(self, attrs):
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "brand", "price", "image"]
        read_only_fields = ["id", "image"]


class ProductDetailSerializer(ProductSerializer):
    properties = NoValidationPropSerializer(
        many=True,
        required=False,
    )

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            "description",
            "stock",
            "category",
            "properties",
        ]

    # Helper function to assign props to product
    def _assign_props(self, props, product):
        """Assign properties to the product"""
        for prop in props:
            # Ensure no property name duplication
            if product.properties.filter(name__iexact=prop["name"]):
                msg = f"Product can't have two properties with the same name ({prop['name']})!"
                raise serializers.ValidationError(msg)

            # Find existing prop or create new one
            prop_obj, created = Property.objects.get_or_create(
                name__iexact=prop["name"],
                value__iexact=prop["value"],
                defaults={"name": prop["name"], "value": prop["value"]},
            )

            # .add() auto saves changes so no need to call .save() manually
            product.properties.add(prop_obj)

    # Modify creation to create product with props
    def create(self, validated_data):
        """Create product with properties"""
        # Firstly create product without props
        props = validated_data.pop("properties", [])
        product = Product.objects.create(**validated_data)
        # Then create and assign props separately cuz
        # serializer doesn't save nested serializer
        self._assign_props(props, product)

        return product

    def update(self, instance, validated_data):
        """Update product with props"""
        props = validated_data.pop("properties", None)
        super().update(instance, validated_data)

        # Entirely reassign props field if there's "properties" key
        if props is not None:
            instance.properties.clear()
            self._assign_props(props, instance)

        return instance


# Simplified one to return only product id and image in response
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": True}}
