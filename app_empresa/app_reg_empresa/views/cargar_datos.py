# from
#
# @login_required
# def cargar_datos_iniciales(request):
#     """
#     Vista para cargar los datos iniciales del sistema
#     """
#     resultado = {
#         'status': 'success',
#         'message': ''
#     }
#
#     try:
#         # Cargar tipos de costo
#         num_tipos = cargar_tipos_costo_iniciales()
#         resultado['message'] = f'Se han cargado {num_tipos} tipos de costo correctamente.'
#     except Exception as e:
#         resultado['status'] = 'error'
#         resultado['message'] = f'Error al cargar datos iniciales: {str(e)}'
#
#     return JsonResponse(resultado)