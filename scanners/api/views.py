from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..scanners.dorks import main

@api_view(['GET'])
def busqueda_dork(request):
    try:
        query = request.GET.get('q', '') #obtengo parametro url
        resultados = main(query)         #llamo funcion main y le paso el query
        return Response({"Resultados": resultados})
    except Exception as e:
        return Response({"error":str(e)}, status=400)