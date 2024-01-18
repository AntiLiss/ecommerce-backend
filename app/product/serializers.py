from rest_framework import serializers
from .models import Category, Product, Property, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]


# To use when dealing directly with "Property" resource
class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ["id", "name", "value"]
        read_only_fields = ["id"]

    # Check combination of name and value is unique
    def validate(self, attrs):
        property = Property.objects.filter(
            name__iexact=attrs.get("name"),
            value__iexact=attrs.get("value"),
        )

        if property:
            msg = (
                f"Property with this Name ({attrs['name']}) "
                f"and Value ({attrs['value']}) already exists!"
            )
            raise serializers.ValidationError(msg)

        return attrs


# To use inside Product as nested serializer.
# Skips duplication check cuz there's used get_or_create
class NoValidationPropSerializer(PropertySerializer):
    """Property serializer without validation of duplication"""

    # Override to remove validation
    def validate(self, attrs):
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "price",
            "image",
            "rating",
        ]
        read_only_fields = ["id", "image", "rating"]


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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ProductSerializer.Meta.read_only_fields + [
            "created_at",
            "updated_at",
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

    # Modify update to update product with props
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


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "commentary",
            "user",
            "product",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "user", "created_at", "updated_at"]

    # Check for unique constraint violation before creation
    def create(self, validated_data):
        user_id = validated_data.get("user")
        product_id = validated_data.get("product")

        # Return error if the user already wrote review for the product
        if Review.objects.filter(user=user_id, product=product_id):
            msg = "You already wrote review for this product!"
            raise serializers.ValidationError(msg)

        return super().create(validated_data)

    # Prevent updating field "product"
    # TODO Indicate in api docs that "product" field is not available when PATCH and PUT
    def update(self, instance, validated_data):
        validated_data.pop("product", None)
        return super().update(instance, validated_data)
