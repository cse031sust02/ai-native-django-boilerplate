import redis
from django.conf import settings
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        checks = {
            "database": self._check_database(),
            "redis": self._check_redis(),
        }
        healthy = all(v == "ok" for v in checks.values())
        return Response(
            {"status": "ok" if healthy else "degraded", "checks": checks},
            status=200 if healthy else 503,
        )

    def _check_database(self) -> str:
        try:
            connection.ensure_connection()
            return "ok"
        except Exception:
            return "unavailable"

    def _check_redis(self) -> str:
        try:
            client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
            client.ping()
            return "ok"
        except Exception:
            return "unavailable"
