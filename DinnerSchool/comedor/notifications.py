from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def notificar_nuevo_pedido(orden):
    """
    Avisa en vivo (WebSocket) a quien tenga abierto el kanban de que entró
    una orden nueva: pedido de alumno/profesor o venta directa.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    if orden.esVentaDirecta:
        titulo = orden.clienteNombre or 'Venta Directa'
        subtitulo = 'Venta Directa'
    elif orden.profesorId:
        titulo = f"{orden.profesorId.usuario.nombre} {orden.profesorId.usuario.paterno}"
        subtitulo = 'Profesor'
    elif orden.alumnoId:
        titulo = f"{orden.alumnoId.nombre} {orden.alumnoId.paterno}"
        subtitulo = 'Alumno'
    else:
        titulo = 'Pedido nuevo'
        subtitulo = ''

    async_to_sync(channel_layer.group_send)(
        'kanban_notifications',
        {
            'type': 'nuevo_pedido',
            'data': {
                'orden_id': orden.id,
                'titulo': titulo,
                'subtitulo': subtitulo,
                'turno': orden.get_turno_label(),
                'total': str(orden.total),
                'es_venta_directa': orden.esVentaDirecta,
            },
        },
    )
