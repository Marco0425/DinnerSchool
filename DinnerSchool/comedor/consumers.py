import json

from channels.generic.websocket import AsyncWebsocketConsumer

from core.models import Empleados


class KanbanConsumer(AsyncWebsocketConsumer):
    """
    Notifica en vivo al admin/cocina cuando entra un pedido o venta directa nueva.
    Solo se conectan usuarios staff o empleados (mismo criterio que ve el kanban).
    """
    GROUP_NAME = 'kanban_notifications'

    async def connect(self):
        user = self.scope.get('user')

        if not user or not user.is_authenticated:
            await self.close()
            return

        is_allowed = user.is_staff or await self._es_empleado(user)
        if not is_allowed:
            await self.close()
            return

        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def nuevo_pedido(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @staticmethod
    async def _es_empleado(user):
        from asgiref.sync import sync_to_async
        return await sync_to_async(
            Empleados.objects.filter(usuario__email=user.username).exists
        )()
