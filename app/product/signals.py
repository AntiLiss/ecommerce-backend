from django.dispatch import receiver
from django.db.models import Avg
from django.db.models.signals import m2m_changed, post_save, post_delete
from .models import Product, Property, Review


# Prevent adding two props with the same name to product
@receiver(m2m_changed, sender=Product.properties.through)
def check_unique_properties(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        product_props = instance.properties.values_list("name", flat=True)
        product_props_lower = [name.lower() for name in product_props]

        passed_prop_names = []
        for pk in pk_set:
            passed_prop_name = Property.objects.get(pk=pk).name
            passed_prop_name_lower = passed_prop_name.lower()
            passed_prop_names.append(passed_prop_name_lower)

            error_msg = f"Product can have only one property with the same name ({passed_prop_name})!"

            # Check for name duplication of passed props
            if len(passed_prop_names) != len(set(passed_prop_names)):
                raise ValueError(error_msg)

            # Check for name duplication of passed and existing prop
            if passed_prop_name_lower in product_props_lower:
                raise ValueError(error_msg)


# Update product rating whenever review for it saved or deleted
@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_product_rating(sender, instance, created, **kwargs):
    product = instance.product
    reviews = product.review_set.all()
    average_rating_dict = reviews.aggregate(Avg("rating"))
    average_rating = average_rating_dict["rating__avg"]

    # If averate rating is None or 0 then set 0
    product.rating = average_rating or 0
    product.save()
