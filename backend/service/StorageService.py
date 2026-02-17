from typing import Any, Optional, Dict

from backend.Sql.SClient import SupabaseClient


class StorageService:
    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    def _extract_value(self, data: Any, keys: tuple) -> Optional[str]:
        if isinstance(data, dict):
            for key in keys:
                value = data.get(key)
                if value:
                    return value
            inner = data.get("data")
            if isinstance(inner, dict):
                for key in keys:
                    value = inner.get(key)
                    if value:
                        return value
        if hasattr(data, "get"):
            try:
                for key in keys:
                    value = data.get(key)
                    if value:
                        return value
            except Exception:
                pass
        return None

    async def create_url(
        self,
        bucket: str,
        path: str,
        operation: str = "download",
        expires_in: int = 3600,
    ) -> Dict[str, Any]:
        if not bucket or not path:
            raise ValueError("bucket and path are required")
        op = (operation or "download").lower()
        if expires_in <= 0:
            raise ValueError("expires_in must be positive")

        storage = self.sb.client.storage.from_(bucket)
        if op in ("upload", "signed_upload", "signed-upload", "upload_signed"):
            result = storage.create_signed_upload_url(path)
        elif op in ("public", "public_url", "public-url"):
            result = storage.get_public_url(path)
        else:
            op = "download"
            result = storage.create_signed_url(path, expires_in)

        url = self._extract_value(
            result,
            (
                "signedUrl",
                "signedURL",
                "signed_url",
                "publicUrl",
                "publicURL",
                "public_url",
                "url",
            ),
        )
        if not url:
            raise RuntimeError("failed to create storage url")

        token = self._extract_value(result, ("token",))

        data: Dict[str, Any] = {
            "bucket": bucket,
            "path": path,
            "operation": op,
            "url": url,
        }
        if op == "download":
            data["expires_in"] = expires_in
        if token:
            data["token"] = token
        return data
