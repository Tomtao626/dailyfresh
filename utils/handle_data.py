from django.http import QueryDict


def body_data_handle(request):
    data = QueryDict(request, mutable=True)
    return data