from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError 
from rest_framework.response import Response
from .models import CashFlow, GuideFactory, guides_kw
from .serializer import CashFlowSerializer

class GuideAPIView(APIView):

    def get(self, request, type, obj_id=None):
        model = guides_kw[type]
        
        factory = GuideFactory(guide=model)
        if not obj_id:
            objects_list = factory.get_all_list()
            if type == 'subcategorys':
                # Почва для оптимизации: скорее всего возникает проблема с запросами N + 1
                response_data = [
                    {'id': element.id, 'name': element.name, 'category': element.category.name}
                    for element in objects_list
                ]
            else:
                response_data = [
                    {'id': element.id, 'name': element.name}
                    for element in objects_list
                ]
            return Response(
                status=status.HTTP_200_OK, 
                data={'list': response_data}
                )
        else:
            data_object = factory.get_guide(obj_id)
            if type == 'subcategorys':
                response_data = {
                    'id': data_object.id,
                    'name': data_object.name,
                    'category': data_object.category.name
                }
            else:
                response_data = {
                    'id': data_object.id,
                    'name': data_object.name
                }
            return Response(
                status=status.HTTP_200_OK,
                data=response_data
            )
    
    @transaction.atomic
    def post(self, request, type):
        sid = transaction.savepoint()
        try:
            data = request.data
            if 'name' not in data:
                raise ValidationError({'name': 'Field is required.'})
            if type == 'subcategorys' and not 'category' in data:
                transaction.savepoint_rollback(sid)
                raise ValidationError({'category': 'Field is required for subcategorys.'})
            model = guides_kw[type]
            factory = GuideFactory(model)

            element = factory.create_element(data)
            transaction.savepoint_commit(data)
            return Response(
                status=status.HTTP_201_CREATED,
                data={
                    'name': element.name,
                    'id': element.id
                }
            )
        except ValidationError as e:
            transaction.savepoint_rollback(sid)
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'msg': f'Validation error: {str(e)}.'
                }
            )
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={'msg': 'Internal server error, try later.'}
            )
    
    @transaction.atomic
    def patch(self, request, type, obj_id):
        sid = transaction.savepoint()
        try:
            data = request.data
            if 'name' not in data:
                raise ValidationError({'name': 'Field is required.'})
            
            allowed_fields = {'name', 'category'}
            invalid_fields = set(data.keys()) - allowed_fields
            if invalid_fields:
                raise ValidationError({f'Your request has inncorrect fields: {", ".join(invalid_fields)}'})

            model = guides_kw[type]
            factory = GuideFactory(model)

            object = factory.update_name_or_category(obj_id, data)
            transaction.savepoint_commit(sid)
            response_data = {
                'id': object.id,
                'name': object.name
            }
            if object.category:
                response_data['category'] = object.category
            return Response(
                status=status.HTTP_200_OK,
                data={
                    'updated': response_data
                }
            )
        except ValidationError as e:
            transaction.savepoint_rollback(sid)
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'msg': f'Validation error: {e}.'
                }
            )
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'msg': 'Internal server error, try later.'
                }
            )

    @transaction.atomic
    def delete(self, request, type, obj_id):
        sid = transaction.savepoint()
        try:
            model = guides_kw[type]
            factory = GuideFactory(model)
            if not factory.get_name(obj_id):
                transaction.savepoint_rollback(sid)
                raise ValidationError('Object does not exist.')
            else:
                factory.delete_element(obj_id)
            return Response(
                status=status.HTTP_200_OK,
                data={
                    'msg': 'success'
                }
            )
        except (ObjectDoesNotExist, ValidationError) as e:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={
                    'msg': 'Object not found.'
                }
            )
        except Exception as e:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={
                    'msg': 'Internal server error, try later.'
                }
            )


class CashFlowGenericAPIView(generics.ListCreateAPIView):
    queryset = CashFlow.objects.all()
    serializer_class = CashFlowSerializer
    ordering_fields = ['created_at', 'updated_at', 'id']
    ordering = ['-created_at']

    def get_queryset(self):
        return CashFlow.objects.select_related(
            'type',
            'status',
            'category__category'
        ).order_by('-created_at')
    