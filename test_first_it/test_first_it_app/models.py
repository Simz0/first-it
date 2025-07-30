import uuid
from datetime import date
from django.utils import timezone
from django.db import models


class StatusType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='Статус ДДС')

    def __str__(self):
        return self.name
    

class OperationType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='Тип ДДС')

    def __str__(self):
        return self.name
    

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class Subcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='sub_categorys')

    class Meta:
        unique_together = (('name', 'category',),) # Для каждой субкатегории только одная категория

    def __str__(self):
        return self.name


class CashFlowQuerySet(models.QuerySet):
    def with_relations(self):
        return self.select_related(
            'category__category',
            'type',
            'status',
        )
    
    def get(self, *args, **kwargs):
        return self.with_relations().get(*args, **kwargs)
    
    def filter(self, *args, **kwargs):
        return self.with_relations().filter(*args, **kwargs)


class CashFlowManager(models.Manager):
    def get_queryset(self):
        return CashFlowQuerySet(self.model, using=self._db)
    
    def with_relations(self):
        self.get_queryset().with_relations()
    
    def get(self, *args, **kwargs):
        return self.get_queryset().get(*args, **kwargs)
    
    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)
    

class CashFlow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.IntegerField()
    comment = models.CharField(max_length=255, null=True)
    created_at = models.DateField(default=date.today)
    category = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='categorys')
    type = models.ForeignKey(OperationType, on_delete=models.CASCADE, related_name='types')
    status = models.ForeignKey(StatusType, on_delete=models.CASCADE, related_name='statuses')

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "comment": self.comment,
            "created_at": str(self.created_at),
            "category": {
                self.category.name,
                self.category.category.name,
            },
            "type": str(self.type),
            "status": str(self.status),
        }
    
    objects = CashFlowManager

guides_kw = {
    'operations': OperationType,
    'categories': Category,
    'subcategories': Subcategory,
    'statuses': StatusType
}

class GuideFactory:
    def __init__(self, guide: StatusType | Subcategory | Category | OperationType):
        self.guide = guide

    def get_guide(self, id: uuid):
        return self.guide.objects.get(id=id)
    
    def delete_element(self, element_id):
        self.guide.objects.delete(id=element_id)
    
    def create_element(self, data: {'name': str} | {'name': str, 'category': uuid}):
        if type(self.guide) != Subcategory: 
            new_object = self.guide.objects.create(
                name=data['name']
            )
        else:
            category = Category.objects.get(id=data['category'])
            new_object = self.guide.objects.create(
                name=data['name'],
                category=category
            )

        return new_object
    
    def update_name_or_category(self, id: str, data: dict['name': str] | dict['category': str] | dict['name': str, 'category': str]):
        if 'category' in data:
            category = Category.objects.get(id=data['category'])
            data['category'] = category
            return self.guide.objects.update(
                id=id,
                **data
            )
        else:
            return self.guide.objects.update(id=id, **data)

    def get_name(self, id: str):
        return self.guide.objects.get(id=id).name
    
    def get_all_list(self):
        return self.guide.objects.all()