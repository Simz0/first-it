from django.core.management.base import CommandError
from .models import StatusType, OperationType, Category, Subcategory

def create_initial_data(verbose=True):
    statuses = ['Бизнес', 'Личное', 'Налог']
    for name in statuses:
        StatusType.objects.get_or_create(name=name)
        if verbose:
            print(f"Status: {name}")

    operation_types = ['Пополнение', 'Списание']
    for name in operation_types:
        OperationType.objects.get_or_create(name=name)
        if verbose:
            print(f"Operation type: {name}")

    categories = {
        'Инфраструктура': ['VPS', 'Proxy'],
        'Маркетинг': ['Farpost', 'Avito'],
    }
    
    for category_name, subcategories in categories.items():
        category, created = Category.objects.get_or_create(name=category_name)
        if verbose and created:
            print(f"Category: {category_name}")
        
        for sub_name in subcategories:
            Subcategory.objects.get_or_create(
                name=sub_name, 
                category=category
            )
            if verbose:
                print(f"Subcategory: {sub_name}")
    
    required_items = [
        (StatusType, 3),
        (OperationType, 2),
        (Category, 2),
        (Subcategory, 4),
    ]
    
    for model, expected_count in required_items:
        count = model.objects.count()
        if count < expected_count:
            raise CommandError(f"Error for {model.__name__} create {count} elements instead of {expected_count}")
    
    if verbose:
        print("\nStart data created complete!")